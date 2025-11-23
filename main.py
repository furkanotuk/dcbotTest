import discord
import os
import random
from discord.ext import commands
from discord import app_commands

# Tokeni environment variable'dan çekiyoruz
TOKEN = os.getenv('DISCORD_TOKEN')

# Intent ayarları
intents = discord.Intents.default()
intents.message_content = True

# Bot kurulumu
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Bot Giriş Yaptı: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'------------------------------------')
    
    # Slash komutlarını Discord'a senkronize ediyoruz
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)} adet slash komutu senkronize edildi.')
    except Exception as e:
        print(f'Senkronizasyon hatası: {e}')

# --- TEMEL KOMUTLAR ---

@bot.tree.command(name="ping", description="Botun gecikme süresini ölçer.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'🏓 Pong! Gecikme: {latency}ms 🚀')

@bot.tree.command(name="whoami", description="Bot hakkında bilgi verir.")
async def whoami(interaction: discord.Interaction):
    await interaction.response.send_message(f'🚀 Merhaba! Ben Genelsoft sunucusu üzerinde barındırılan, slash komutlarıyla çalışan modern bir Discord botuyum.')

# --- EĞLENCELİ KOMUTLAR ---

@bot.tree.command(name="sansli_sayi", description="Sana özel şanslı bir sayı üretir.")
async def sansli_sayi(interaction: discord.Interaction):
    sayi = random.randint(1, 100)
    await interaction.response.send_message(f'🍀 {interaction.user.mention}, bugünkü şanslı sayın: **{sayi}**')

@bot.tree.command(name="yazi_tura", description="Yazı mı Tura mı? Şansını dene.")
async def yazi_tura(interaction: discord.Interaction):
    sonuc = random.choice(["Yazı", "Tura"])
    await interaction.response.send_message(f'🪙 Para havada... Ve sonuç: **{sonuc}**!')

@bot.tree.command(name="secim_yap", description="İki seçenek arasında kararsız mı kaldın?")
@app_commands.describe(secenek1="İlk seçenek", secenek2="İkinci seçenek")
async def secim_yap(interaction: discord.Interaction, secenek1: str, secenek2: str):
    secim = random.choice([secenek1, secenek2])
    await interaction.response.send_message(f'🤔 Hımm... Bence **{secim}** daha mantıklı!')

@bot.tree.command(name="saril", description="Birine sanal olarak sarıl.")
@app_commands.describe(kullanici="Sarılmak istediğin kullanıcı")
async def saril(interaction: discord.Interaction, kullanici: discord.User):
    await interaction.response.send_message(f'🤗 {interaction.user.mention}, {kullanici.mention} kullanıcısına kocaman sarıldı!')

# --- REHBER KOMUTU ---

@bot.tree.command(name="rehber", description="Discord Bot Barındırma ve Kurulum Rehberi")
async def rehber(interaction: discord.Interaction):
    metin = """
## 🚀 Discord Bot Barındırma Hizmeti Rehberi

Discord botunuzu sistemimize entegre etmek için aşağıdaki adımları takip ediniz:

1. **GitHub Hazırlığı:** Botunuz için sabitlenmiş mesajdaki görseldeki yapıyı kurup GitHub'a **public repository** olarak yüklemeniz gerekmektedir.
2. **Dockerfile:** Bu yapıyı kurabilmek için kullandığınız yapay zekaya şu komutu verin:
   > *"Botumu Coolify üzerinde deploy edeceğim. Bunun için bir Dockerfile hazırlar mısın?"*
3. **Environment (Token) Ayarları:** Bot Token güvenliği çok kritiktir. Yapay zekaya şu soruyu sorun:
   > *"Token gibi önemli variable'ları Coolify environment'e entegre çalışacak şekilde düzenleyip bana anlatır mısın?"*

⚠️ **DİKKAT:** Tokeninizi kod içine (hardcoded) yazmayınız. Bunu yapmazsanız GitHub üzerindeki kötü niyetli tarayıcılar tokeninizi çalar ve sunucunuza zarar verebilir. Değişkenleri Coolify paneli üzerinden ekleyeceğiz.

---
**Fiyatlandırma:**
* **Başlangıç:** 1 Ay Bedava
* **Standart Tarife:** Aylık 30 TL
* **Premium/Kurumsal:** Aylık 250 TL
    """
    await interaction.response.send_message(metin)

if __name__ == "__main__":
    if not TOKEN:
        print("Hata: DISCORD_TOKEN bulunamadı! Coolify Environment kısmını kontrol et.")
    else:
        bot.run(TOKEN)