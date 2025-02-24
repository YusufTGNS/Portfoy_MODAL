# Proje Yönetim Botu (Discord)

Bu proje, Discord botu kullanarak proje yönetimi yapmayı sağlayan bir sistemdir. Kullanıcılar, projeler ekleyebilir, mevcut projeleri görüntüleyebilir ve düzenleyebilirler. Bot SQLite veritabanını kullanarak projelerin bilgilerini saklar.

## Özellikler
- **Yeni Proje Oluşturma**: Kullanıcılar, proje adı, açıklaması, URL'si ve kullanılan becerilerle yeni projeler oluşturabilir.
- **Proje Bilgilerini Görüntüleme**: Kullanıcılar, mevcut projelerin bilgilerini görüntüleyebilir.
- **Proje Düzenleme**: Kullanıcılar, mevcut bir projenin açıklamasını, URL'sini ve becerilerini güncelleyebilir.
- **Proje Silme**: Kullanıcılar, mevcut bir projelerini silebilir.
- **Veritabanı Yönetimi**: Proje bilgileri SQLite veritabanında saklanır ve kolayca erişilebilir.
- !new_project
- !delete_project
- !get_project
- !projects
- !edit_project

## Gereksinimler
Projenin çalışabilmesi için aşağıdaki Python kütüphanelerinin kurulu olması gerekmektedir:
- `discord.py`
- `sqlite3`

Projeyi çalıştırmadan önce bu kütüphaneleri yüklemeniz gerekir. Gereksinimleri yüklemek için aşağıdaki komutu kullanabilirsiniz:

```bash
pip install discord.py
