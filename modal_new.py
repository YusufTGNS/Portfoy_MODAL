import discord
from discord.ext import commands
from discord import ui, ButtonStyle, TextStyle, Embed
from config import TOKEN
import uuid
import sqlite3

# Veritabanı işlemleri için yardımcı sınıf
class DatabaseHandler:
    @staticmethod
    def execute_query(query, params=(), fetchone=False, fetchall=False):
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        try:
            c.execute(query, params)
            if fetchone:
                result = c.fetchone()
            elif fetchall:
                result = c.fetchall()
            else:
                conn.commit()
                result = None
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            result = None
        finally:
            conn.close()
        return result

# Veritabanını oluştur
DatabaseHandler.execute_query('''CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, 
                    user_id TEXT, 
                    project_name TEXT, 
                    project_desc TEXT, 
                    project_url TEXT, 
                    project_skills TEXT,
                    project_status TEXT)''')

# Modal Penceresi
class ProjectModal(ui.Modal, title='Yeni Proje'):
    project_name = ui.TextInput(label='Proje Adı')
    project_desc = ui.TextInput(label='Proje Açıklaması', style=TextStyle.paragraph)
    project_url = ui.TextInput(label='Proje URL')
    project_skills = ui.TextInput(label='Projede Kullanılan Beceriler', style=TextStyle.paragraph)
    project_status = ui.TextInput(label='Proje Durumu', style=TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.project_name.value.strip():
            await interaction.response.send_message("Proje adı boş olamaz!", ephemeral=True)
            return
        project_id = str(uuid.uuid4())
        user_id = str(interaction.user.id)  # Kullanıcının Discord ID'sini al
        DatabaseHandler.execute_query(
            'INSERT INTO projects (id, user_id, project_name, project_desc, project_url, project_skills, project_status) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (project_id, user_id, self.project_name.value, self.project_desc.value, self.project_url.value, self.project_skills.value, self.project_status.value)
        )
        await interaction.response.send_message(f'Proje başarıyla kaydedildi!\nProje ID: {project_id}', ephemeral=True)

class NewProjectButton(ui.Button):
    def __init__(self):
        super().__init__(label="Yeni Proje Oluştur", style=ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ProjectModal())

class ProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NewProjectButton())

class ProjectIDModal(ui.Modal, title='Proje ID Girin'):
    project_id = ui.TextInput(label='Proje ID')

    async def on_submit(self, interaction: discord.Interaction):
        project = DatabaseHandler.execute_query('SELECT * FROM projects WHERE id = ?', (self.project_id.value,), fetchone=True)
        if project:
            # Proje kullanıcıya ait mi kontrol et
            if project[1] != str(interaction.user.id):
                await interaction.response.send_message("Bu projeye erişim izniniz yok.", ephemeral=True)
                return
            embed = Embed(title=f"Proje: {project[2]}", description=project[3], color=discord.Color.blurple())
            embed.add_field(name="Proje URL", value=project[4], inline=False)
            embed.add_field(name="Projede Kullanılan Beceriler", value=project[5], inline=False)
            embed.add_field(name="Proje Durumu", value=project[6], inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"ID '{self.project_id.value}' ile bir proje bulunamadı.", ephemeral=True)

class GetProjectButton(ui.Button):
    def __init__(self):
        super().__init__(label="Proje Bilgilerini Getir", style=ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ProjectIDModal())

class GetProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GetProjectButton())

class EditProjectModal(ui.Modal, title='Proje Düzenleme'):
    project_id = ui.TextInput(label='Proje ID')
    project_desc = ui.TextInput(label='Yeni Proje Açıklaması', style=TextStyle.paragraph, required=False)
    project_url = ui.TextInput(label='Yeni Proje URL', required=False)
    project_skills = ui.TextInput(label='Yeni Projede Kullanılan Beceriler', required=False)
    project_status = ui.TextInput(label='Yeni Proje Durumu', required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Proje ID'sinin veritabanında var olup olmadığını kontrol et
        project = DatabaseHandler.execute_query('SELECT * FROM projects WHERE id = ?', (self.project_id.value,), fetchone=True)
        
        if not project:
            await interaction.response.send_message(f"ID '{self.project_id.value}' ile bir proje bulunamadı. Lütfen geçerli bir proje ID'si girin.", ephemeral=True)
            return

        # Proje kullanıcıya ait mi kontrol et
        if project[1] != str(interaction.user.id):
            await interaction.response.send_message("Bu projeyi düzenleme izniniz yok.", ephemeral=True)
            return

        # Eğer proje bulunursa, güncelleme işlemini gerçekleştir
        updates = {}
        if self.project_desc.value:
            updates['project_desc'] = self.project_desc.value
        if self.project_url.value:
            updates['project_url'] = self.project_url.value
        if self.project_skills.value:
            updates['project_skills'] = self.project_skills.value
        if self.project_status.value:
            updates['project_status'] = self.project_status.value

        if updates:
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            params = list(updates.values()) + [self.project_id.value]
            DatabaseHandler.execute_query(f'UPDATE projects SET {set_clause} WHERE id = ?', params)
            await interaction.response.send_message(f'Proje ID: {self.project_id.value} başarıyla güncellendi!', ephemeral=True)
        else:
            await interaction.response.send_message('Herhangi bir değişiklik yapılmadı.', ephemeral=True)

class EditProjectButton(ui.Button):
    def __init__(self):
        super().__init__(label="Proje Düzenle", style=ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditProjectModal())

class EditProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(EditProjectButton())

# Yeni Modal: Proje Silme
class DeleteProjectModal(ui.Modal, title='Proje Sil'):
    project_id = ui.TextInput(label='Proje ID')

    async def on_submit(self, interaction: discord.Interaction):
        # Proje ID'sinin veritabanında var olup olmadığını kontrol et
        project = DatabaseHandler.execute_query('SELECT * FROM projects WHERE id = ?', (self.project_id.value,), fetchone=True)
        
        if not project:
            await interaction.response.send_message(f"ID '{self.project_id.value}' ile bir proje bulunamadı. Lütfen geçerli bir proje ID'si girin.", ephemeral=True)
            return

        # Proje kullanıcıya ait mi kontrol et
        if project[1] != str(interaction.user.id):
            await interaction.response.send_message("Bu projeyi silme izniniz yok.", ephemeral=True)
            return

        # Proje silme işlemi
        DatabaseHandler.execute_query('DELETE FROM projects WHERE id = ?', (self.project_id.value,))
        await interaction.response.send_message(f'Proje ID: {self.project_id.value} başarıyla silindi!', ephemeral=True)

class DeleteProjectButton(ui.Button):
    def __init__(self):
        super().__init__(label="Proje Sil", style=ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DeleteProjectModal())

class DeleteProjectView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DeleteProjectButton())

# Bot Tanımlama
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı')

@bot.command()
async def new_project(ctx):
    await ctx.send("Aşağıdaki butona tıklayarak yeni bir proje oluşturabilirsiniz:", view=ProjectView())

@bot.command()
async def edit_project(ctx):
    await ctx.send("Aşağıdaki butona tıklayarak düzenlemek istediğiniz projeyi seçebilirsiniz:", view=EditProjectView())

@bot.command()
async def delete_project(ctx):
    await ctx.send("Aşağıdaki butona tıklayarak silmek istediğiniz projeyi seçebilirsiniz:", view=DeleteProjectView())

@bot.command()
async def projects(ctx):
    projects = DatabaseHandler.execute_query('SELECT id, project_name FROM projects', fetchall=True)
    if projects:
        embed = Embed(title="Projeler", description="Mevcut Projeler", color=discord.Color.blue())
        for project in projects:
            embed.add_field(name=f'ID: {project[0]}', value=project[1], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Henüz herhangi bir proje bulunmuyor.")

@bot.command()
async def get_project(ctx):
    await ctx.send("Aşağıdaki butona tıklayarak proje bilgilerini alabilirsiniz:", view=GetProjectView())

bot.run(TOKEN)
