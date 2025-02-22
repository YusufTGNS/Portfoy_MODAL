import discord
from discord.ext import commands
from discord import ui, ButtonStyle, TextStyle
import sqlite3
from config import TOKEN

# Veritabanı işlemleri
def create_database():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_project_to_db(name, description, date):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO projects (name, description, date)
        VALUES (?, ?, ?)
    ''', (name, description, date))
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('SELECT name, description, date FROM projects')
    projects = c.fetchall()
    conn.close()
    return projects

# Botu oluşturuyoruz
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Modal pencere tanımlama
class TestModal(ui.Modal, title='Proje Bilgilerini Girin'):
    name_field = ui.TextInput(label='Proje Adı')
    description_field = ui.TextInput(label='Proje Açıklaması', style=TextStyle.paragraph)
    date_field = ui.TextInput(label='Proje Tarihi (YYYY-MM-DD)')

    async def on_submit(self, interaction: discord.Interaction):
        add_project_to_db(self.name_field.value, self.description_field.value, self.date_field.value)
        await interaction.user.send(f'Proje başarıyla eklendi!\n'
                                     f'Proje Adı: {self.name_field.value}\n'
                                     f'Açıklama: {self.description_field.value}\n'
                                     f'Tarih: {self.date_field.value}')

        if not interaction.response.is_done():
            await interaction.response.defer()

# Buton tanımlama
class TestButton(ui.Button):
    def __init__(self, label="Proje Ekle", style=ButtonStyle.blurple, row=0):
        super().__init__(label=label, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        await interaction.user.send("Proje eklemek için gerekli bilgileri girin.")
        await interaction.response.send_modal(TestModal())

        self.style = ButtonStyle.gray
        if not interaction.response.is_done():
            await interaction.response.defer()

# Projeleri görüntüleme
@bot.command()
async def projects(ctx):
    projects = get_all_projects()
    if projects:
        embed = discord.Embed(title="Eklenen Projeler")
        for project in projects:
            embed.add_field(name=project[0], value=f"Açıklama: {project[1]}\nTarih: {project[2]}", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Hiç proje eklenmedi.")

# Komutlar komutu
@bot.command()
async def komutlar(ctx):
    komut_listesi = """
    **Mevcut Komutlar:**
    1. `!test` - Proje eklemek için modal pencereyi açar.
    2. `!projects` - Eklenen projeleri listeler.
    3. `!komutlar` - Mevcut komutları listeler.
    """
    await ctx.send(komut_listesi)

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class TestView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TestButton(label="Proje Ekle"))

# Bot hazır olduğunda gönderilen bir olay
@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı')

# Butonu gösteren bir komut
@bot.command()
async def test(ctx):
    await ctx.send("Aşağıdaki butona tıklayın:", view=TestView())

# Veritabanını oluşturuyoruz
create_database()

# Botu başlatıyoruz
bot.run(TOKEN)
