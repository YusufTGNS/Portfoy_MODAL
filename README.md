# Discord Bot - Proje Yönetimi

Bu proje, Discord sunucularında kullanıcıların projeleri ekleyip, projelerini listeleyebileceği bir botu içerir. Bot, kullanıcıların projelerini veritabanına kaydedip, eklenen projeleri görüntülemelerini sağlar. Ayrıca, kullanıcılar mevcut komutları öğrenebilir.

## Özellikler

- **Proje Ekleme**: Kullanıcılar, bot üzerinden proje adı, açıklaması ve tarihi girerek projelerini ekleyebilir.
- **Projeleri Görüntüleme**: Eklenen projeler, `!projects` komutuyla görüntülenebilir.
- **Komutlar**: `!komutlar` komutu ile mevcut bot komutları kullanıcıya listelenebilir.

## Kullanılan Teknolojiler

- Python 3.x
- Discord.py kütüphanesi
- SQLite3 (Veritabanı)

## Kurulum

### 1. Python ve Bağımlılıkları Yükleme

Öncelikle Python 3.x sürümünü bilgisayarınızda kurmanız gerekiyor. Ardından, Discord.py kütüphanesini yüklemek için terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:

```bash
pip install discord.py
