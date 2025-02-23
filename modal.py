import discord
from discord.ext import commands
from discord import ui, ButtonStyle, TextStyle, Embed
from config import TOKEN
import uuid  # Benzersiz ID oluşturmak için
import sqlite3  # SQLite veritabanı

# SQLite veritabanı bağlantısı ve tablo oluşturma
def create_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Tabloyu oluştur
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, 
                    project_name TEXT, 
                    project_desc TEXT, 
                    project_url TEXT, 
                    project_skills TEXT)''')
    conn.commit()
    conn.close()

# Modal pencere tanımlama
class ProjectModal(ui.Modal, title='Yeni Proje'):
    # Modal pencerede metin alanları tanımlama
    project_name = ui.TextInput(label='Proje Adı')
    project_desc = ui.TextInput(label='Proje Açıklaması', style=TextStyle.paragraph)
    project_url = ui.TextInput(label='Proje URL')
    project_skills = ui.TextInput(label='Projede Kullanılan Beceriler', style=TextStyle.paragraph)

    # Modal pencere istendiğinde çağrılan bir yöntem
    async def on_submit(self, interaction: discord.Interaction):
        project_id = str(uuid.uuid4())  # Benzersiz ID oluşturma
        
        # Veritabanına kaydetme
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('INSERT INTO projects (id, project_name, project_desc, project_url, project_skills) VALUES (?, ?, ?, ?, ?)', 
                  (project_id, self.project_name.value, self.project_desc.value, self.project_url.value, self.project_skills.value))
        conn.commit()
        conn.close()

        # Kullanıcıya işlem tamamlandığını bildirme
        await interaction.response.send_message(f'Proje başarıyla kaydedildi!\nProje ID: {project_id}', ephemeral=True)

# Buton tanımlama
class NewProjectButton(ui.Button):
    def __init__(self, label="Yeni Proje Oluştur", style=ButtonStyle.blurple, row=0):
        super().__init__(label=label, style=style, row=row)

    # Butona basıldığında çağrılan bir yöntem
    async def callback(self, interaction: discord.Interaction):
        # Modal pencereyi açma
        await interaction.response.send_modal(ProjectModal())

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class ProjectView(ui.View):
    def __init__(self):
        super().__init__()
        # Görünüme bir buton ekleme
        self.add_item(NewProjectButton(label="Yeni Proje Oluştur"))

# Proje ID'si için modal
class ProjectIDModal(ui.Modal, title='Proje ID Girin'):
    project_id = ui.TextInput(label='Proje ID')

    # Modal penceresi gönderildiğinde proje bilgilerini al
    async def on_submit(self, interaction: discord.Interaction):
        project_id = self.project_id.value
        
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = c.fetchone()  # Belirtilen ID'ye ait projeyi al
        conn.close()

        if project:
            embed = Embed(title=f"Proje ID: {project[0]}", description=project[1], color=discord.Color.blurple())
            embed.add_field(name="Proje Açıklaması", value=project[2])
            embed.add_field(name="Proje URL", value=project[3])
            embed.add_field(name="Projede Kullanılan Beceriler", value=project[4])
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = Embed(title="Proje Bulunamadı", description=f"ID '{project_id}' ile bir proje bulunamadı.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Buton tanımlama
class GetProjectButton(ui.Button):
    def __init__(self, label="Proje Bilgilerini Getir", style=ButtonStyle.green, row=0):
        super().__init__(label=label, style=style, row=row)

    # Butona basıldığında çağrılan bir yöntem
    async def callback(self, interaction: discord.Interaction):
        # Proje ID'si için modal pencereyi açma
        await interaction.response.send_modal(ProjectIDModal())

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class GetProjectView(ui.View):
    def __init__(self):
        super().__init__()
        # Görünüme bir buton ekleme
        self.add_item(GetProjectButton(label="Proje Bilgilerini Getir"))

# Proje düzenleme modalı
class EditProjectModal(ui.Modal, title='Proje Düzenleme'):
    project_id = ui.TextInput(label='Proje ID')
    project_desc = ui.TextInput(label='Yeni Proje Açıklaması', style=TextStyle.paragraph, required=False)
    project_url = ui.TextInput(label='Yeni Proje URL', required=False)
    project_skills = ui.TextInput(label='Yeni Projede Kullanılan Beceriler', required=False)

    # Modal pencere istendiğinde çağrılan bir yöntem
    async def on_submit(self, interaction: discord.Interaction):
        project_id = self.project_id.value
        new_desc = self.project_desc.value if self.project_desc.value else None
        new_url = self.project_url.value if self.project_url.value else None
        new_skills = self.project_skills.value if self.project_skills.value else None
        
        # Veritabanında ID'yi kontrol etme
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = c.fetchone()
        
        if not project:
            embed = Embed(title="Hata", description=f"ID '{project_id}' ile bir proje bulunamadı.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return

        # Veritabanındaki projeyi güncelleme
        if new_desc:
            c.execute('UPDATE projects SET project_desc = ? WHERE id = ?', (new_desc, project_id))
        if new_url:
            c.execute('UPDATE projects SET project_url = ? WHERE id = ?', (new_url, project_id))
        if new_skills:
            c.execute('UPDATE projects SET project_skills = ? WHERE id = ?', (new_skills, project_id))
        conn.commit()
        conn.close()

        embed = Embed(title="Proje Güncellendi", description=f'ID: {project_id} başarıyla güncellendi.', color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Edit Project Button
class EditProjectButton(ui.Button):
    def __init__(self, label="Proje Düzenle", style=ButtonStyle.green, row=0):
        super().__init__(label=label, style=style, row=row)

    # Butona basıldığında çağrılan bir yöntem
    async def callback(self, interaction: discord.Interaction):
        # Proje düzenleme modalını açma
        await interaction.response.send_modal(EditProjectModal())

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class EditProjectView(ui.View):
    def __init__(self):
        super().__init__()
        # Görünüme bir buton ekleme
        self.add_item(EditProjectButton(label="Proje Düzenle"))

# Bot yapılandırması
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot hazır olduğunda gönderilen bir olay
@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı')
    create_db()  # Veritabanı ve tabloyu oluştur

# !new_project komutunu tanımlama
@bot.command()
async def new_project(ctx):
    # Yeni proje için buton içeren görünüm ile mesaj gönderme
    await ctx.send("Aşağıdaki butona tıklayarak yeni bir proje oluşturabilirsiniz:", view=ProjectView())

# !projects komutunu tanımlama
@bot.command()
async def projects(ctx):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('SELECT id, project_name FROM projects')
    projects = c.fetchall()  # Proje ID ve Adlarını al
    conn.close()

    if projects:
        embed = Embed(title="Projeler", description="Mevcut Projeler", color=discord.Color.blue())
        for project in projects:
            embed.add_field(name=f'ID: {project[0]}', value=project[1], inline=False)
        await ctx.send(embed=embed)
    else:
        embed = Embed(title="Projeler", description="Henüz herhangi bir proje bulunmuyor.", color=discord.Color.red())
        await ctx.send(embed=embed)

# !get_project komutunu tanımlama
@bot.command()
async def get_project(ctx):
    # Proje bilgilerini getirme butonunu gönder
    await ctx.send("Aşağıdaki butona tıklayarak proje bilgilerini alabilirsiniz:", view=GetProjectView())

# !edit_project komutunu tanımlama
@bot.command()
async def edit_project(ctx):
    # Proje düzenleme için buton içeren görünüm ile mesaj gönderme
    await ctx.send("Aşağıdaki butona tıklayarak düzenlemek istediğiniz projeyi seçebilirsiniz:", view=EditProjectView())

# Botu başlatma
bot.run(TOKEN)
