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

# ==========================================
# 1. MODERASYON VE YÖNETİM KOMUTLARI
# ==========================================

@bot.tree.command(name="at", description="Belirtilen kullanıcıyı sunucudan atar (Kick).")
@app_commands.describe(kullanici="Atılacak kullanıcı", sebep="Atılma sebebi")
@app_commands.checks.has_permissions(kick_members=True)
async def at(interaction: discord.Interaction, kullanici: discord.Member, sebep: str = "Sebep belirtilmedi"):
    if kullanici.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Bu kişinin yetkisi senden yüksek veya eşit, onu atamam Lordum.", ephemeral=True)
        return
    await kullanici.kick(reason=sebep)
    await interaction.response.send_message(f"👢 **{kullanici.name}** sunucudan atıldı. Sebep: {sebep}")

@bot.tree.command(name="yasakla", description="Belirtilen kullanıcıyı sunucudan yasaklar (Ban).")
@app_commands.describe(kullanici="Yasaklanacak kullanıcı", sebep="Yasaklanma sebebi")
@app_commands.checks.has_permissions(ban_members=True)
async def yasakla(interaction: discord.Interaction, kullanici: discord.Member, sebep: str = "Sebep belirtilmedi"):
    if kullanici.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Bu kişinin yetkisi senden yüksek, onu yasaklayamam Lordum.", ephemeral=True)
        return
    await kullanici.ban(reason=sebep)
    await interaction.response.send_message(f"⛔ **{kullanici.name}** yasaklandı! Yargı dağıtıldı. Sebep: {sebep}")

@bot.tree.command(name="yasak_kaldir", description="Kullanıcının yasağını kaldırır (Unban).")
@app_commands.describe(kullanici_id="Yasağı kalkacak kişinin ID'si")
@app_commands.checks.has_permissions(ban_members=True)
async def yasak_kaldir(interaction: discord.Interaction, kullanici_id: str):
    user = await bot.fetch_user(int(kullanici_id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ **{user.name}** adlı kişinin yasağı kaldırıldı.")

@bot.tree.command(name="timeout", description="Kullanıcıya süreli susturma (timeout) uygular.")
@app_commands.describe(kullanici="Susturulacak kişi", dakika="Kaç dakika?")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, kullanici: discord.Member, dakika: int):
    sure = timedelta(minutes=dakika)
    await kullanici.timeout(sure)
    await interaction.response.send_message(f"🤐 **{kullanici.name}**, {dakika} dakika boyunca cezalı köşeye gönderildi.")

@bot.tree.command(name="timeout_kaldir", description="Susturmayı kaldırır.")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_kaldir(interaction: discord.Interaction, kullanici: discord.Member):
    await kullanici.timeout(None)
    await interaction.response.send_message(f"🗣️ **{kullanici.name}** artık konuşabilir.")

@bot.tree.command(name="kanal_kilitle", description="Bulunulan kanalı mesaj gönderimine kapatır.")
@app_commands.checks.has_permissions(manage_channels=True)
async def kanal_kilitle(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Kanal kilitlendi Lordum! Kimse yazamaz.")

@bot.tree.command(name="kanal_ac", description="Kanal kilidini açar.")
@app_commands.checks.has_permissions(manage_channels=True)
async def kanal_ac(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Kanal tekrar erişime açıldı.")

@bot.tree.command(name="rol_ver", description="Bir kullanıcıya rol verir.")
@app_commands.checks.has_permissions(manage_roles=True)
async def rol_ver(interaction: discord.Interaction, kullanici: discord.Member, rol: discord.Role):
    await kullanici.add_roles(rol)
    await interaction.response.send_message(f"✅ **{rol.name}** rolü {kullanici.mention} kişisine verildi.")

@bot.tree.command(name="rol_al", description="Bir kullanıcıdan rol alır.")
@app_commands.checks.has_permissions(manage_roles=True)
async def rol_al(interaction: discord.Interaction, kullanici: discord.Member, rol: discord.Role):
    await kullanici.remove_roles(rol)
    await interaction.response.send_message(f"❌ **{rol.name}** rolü {kullanici.mention} kişisinden alındı.")

# Hata Yönetimi (Yetki Yoksa)
async def permission_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bunu yapmak için yeterli yetkiniz yok Lordum.", ephemeral=True)

at.error(permission_error)
yasakla.error(permission_error)
kanal_kilitle.error(permission_error)

# ==========================================
# 2. BİLGİ VE ANALİZ KOMUTLARI
# ==========================================

@bot.tree.command(name="sunucu_bilgi", description="Sunucu hakkında detaylı bilgi verir.")
async def sunucu_bilgi(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"{guild.name} Bilgileri", color=discord.Color.blue())
    embed.add_field(name="👑 Sahip", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=f"{guild.member_count}", inline=True)
    embed.add_field(name="🆔 Sunucu ID", value=f"{guild.id}", inline=True)
    embed.add_field(name="📅 Oluşturulma", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kullanici_bilgi", description="Bir kullanıcı hakkında bilgi verir.")
async def kullanici_bilgi(interaction: discord.Interaction, kullanici: discord.Member = None):
    kullanici = kullanici or interaction.user
    roller = [rol.mention for rol in kullanici.roles if rol.name != "@everyone"]
    
    embed = discord.Embed(title="Kullanıcı Kimlik Kartı", color=kullanici.color)
    embed.set_thumbnail(url=kullanici.avatar.url if kullanici.avatar else None)
    embed.add_field(name="👤 İsim", value=kullanici.name, inline=True)
    embed.add_field(name="🏷️ Takma Ad", value=kullanici.display_name, inline=True)
    embed.add_field(name="📅 Katılım Tarihi", value=kullanici.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🆔 ID", value=kullanici.id, inline=True)
    embed.add_field(name="🎖️ Roller", value=" ".join(roller) if roller else "Yok", inline=False)
    
    await interaction.response.send_message(embed=embed)


# ==========================================
# 3. ARAÇLAR VE FAYDALI KOMUTLAR
# ==========================================

@bot.tree.command(name="sifre_uret", description="Güçlü bir şifre oluşturur.")
@app_commands.describe(uzunluk="Şifre kaç karakter olsun? (Max 50)")
async def sifre_uret(interaction: discord.Interaction, uzunluk: int = 12):
    if uzunluk > 50: uzunluk = 50
    karakterler = string.ascii_letters + string.digits + "!@#$%^&*"
    sifre = "".join(random.choice(karakterler) for _ in range(uzunluk))
    await interaction.response.send_message(f"🔐 **Oluşturulan Şifre:** ||{sifre}|| \n*(Sadece sen görebilirsin)*", ephemeral=True)

@bot.tree.command(name="matematik", description="Basit matematik işlemleri yapar.")
@app_commands.describe(islem="Topla, Cikar, Carp, Bol", sayi1="İlk sayı", sayi2="İkinci sayı")
@app_commands.choices(islem=[
    app_commands.Choice(name="Toplama (+)", value="topla"),
    app_commands.Choice(name="Çıkarma (-)", value="cikar"),
    app_commands.Choice(name="Çarpma (x)", value="carp"),
    app_commands.Choice(name="Bölme (/)", value="bol")
])
async def matematik(interaction: discord.Interaction, islem: str, sayi1: float, sayi2: float):
    sonuc = 0
    sembol = ""
    if islem == "topla": sonuc, sembol = sayi1 + sayi2, "+"
    elif islem == "cikar": sonuc, sembol = sayi1 - sayi2, "-"
    elif islem == "carp": sonuc, sembol = sayi1 * sayi2, "x"
    elif islem == "bol":
        if sayi2 == 0:
            await interaction.response.send_message("❌ Sıfıra bölemezsin dahi çocuk!", ephemeral=True)
            return
        sonuc, sembol = sayi1 / sayi2, "/"
    
    await interaction.response.send_message(f"🧮 **İşlem:** {sayi1} {sembol} {sayi2} = **{sonuc}**")

@bot.tree.command(name="kelime_say", description="Yazdığın metindeki kelime ve harf sayısını gösterir.")
async def kelime_say(interaction: discord.Interaction, metin: str):
    kelimeler = len(metin.split())
    harfler = len(metin)
    await interaction.response.send_message(f"📝 **Analiz:**\nKelime Sayısı: {kelimeler}\nKarakter Sayısı: {harfler}")

@bot.tree.command(name="yaz", description="Bot ağzından mesaj yazdırır.")
async def yaz(interaction: discord.Interaction, mesaj: str):
    await interaction.response.send_message(f"📨 Mesaj gönderildi.", ephemeral=True)
    await interaction.channel.send(mesaj)

# ==========================================
# 4. EĞLENCE KOMUTLARI (GENİŞLETİLMİŞ)
# ==========================================

@bot.tree.command(name="ask_olc", description="İki kişi arasındaki aşk uyumunu ölçer ❤️")
async def ask_olc(interaction: discord.Interaction, partner: discord.User):
    uyum = random.randint(0, 100)
    emoji = "💔" if uyum < 20 else "😐" if uyum < 50 else "❤️" if uyum < 80 else "🔥"
    
    metin = f"💘 **Aşk Ölçer:**\n{interaction.user.mention} + {partner.mention}\n"
    metin += f"Uyum: **%{uyum}** {emoji}\n"
    
    yorum = "Kaç kurtar kendini!" if uyum < 20 else "Eh işte..." if uyum < 50 else "Çok yakışıyorsunuz!" if uyum < 90 else "EVLENİN HEMEN!"
    
    embed = discord.Embed(description=metin + f"*{yorum}*", color=discord.Color.pink())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="8ball", description="Sihirli küreye bir soru sor.")
async def eightball(interaction: discord.Interaction, soru: str):
    cevaplar = ["Kesinlikle evet.", "Gördüğüm kadarıyla evet.", "Büyük ihtimalle.", "Biraz şüpheli.", 
                "Şu an söyleyemem.", "Tekrar dene.", "Asla.", "Rüyanda görürsün."]
    secilen = random.choice(cevaplar)
    await interaction.response.send_message(f"🎱 **Soru:** {soru}\n🔮 **Cevap:** {secilen}")

@bot.tree.command(name="tas_kagit_makas", description="Bot ile Taş Kağıt Makas oyna.")
@app_commands.choices(secim=[
    app_commands.Choice(name="Taş 🪨", value="tas"),
    app_commands.Choice(name="Kağıt 📜", value="kagit"),
    app_commands.Choice(name="Makas ✂️", value="makas")
])
async def tkm(interaction: discord.Interaction, secim: str):
    bot_secim = random.choice(["tas", "kagit", "makas"])
    sonuc = ""
    
    if secim == bot_secim:
        sonuc = "🤝 Berabere!"
    elif (secim == "tas" and bot_secim == "makas") or \
         (secim == "kagit" and bot_secim == "tas") or \
         (secim == "makas" and bot_secim == "kagit"):
        sonuc = "🎉 Sen kazandın!"
    else:
        sonuc = "🤖 Ben kazandım!"
        
    emoji_map = {"tas": "🪨", "kagit": "📜", "makas": "✂️"}
    await interaction.response.send_message(f"Sen: {emoji_map[secim]} 🆚 Ben: {emoji_map[bot_secim]}\n**Sonuç:** {sonuc}")

@bot.tree.command(name="ters_yazi", description="Yazdığın mesajı tersten yazar.")
async def ters_yazi(interaction: discord.Interaction, metin: str):
    await interaction.response.send_message(f"🔄 {metin[::-1]}")

@bot.tree.command(name="iltifat", description="Kendine veya birine iltifat et.")
async def iltifat(interaction: discord.Interaction, kullanici: discord.User = None):
    sozler = ["Gözlerin yıldızlar gibi parlıyor.", "Bugün harika görünüyorsun!", "Sen bir efsanesin.", 
              "Zekan beni benden alıyor.", "Gülüşün dünyayı aydınlatıyor."]
    hedef = kullanici if kullanici else interaction.user
    await interaction.response.send_message(f"✨ {hedef.mention}, {random.choice(sozler)}")

@bot.tree.command(name="tokat", description="Birini tokatla! (Sanal olarak)")
async def tokat(interaction: discord.Interaction, kurban: discord.User):
    gifler = [
        "https://media.giphy.com/media/Gf3AUz3eBNbSXOEQu4/giphy.gif",
        "https://media.giphy.com/media/xT9IgzFnSqzt2Sp3EI/giphy.gif"
    ]
    embed = discord.Embed(description=f"👋 {interaction.user.mention}, {kurban.mention} kişisine Osmanlı tokadı attı!", color=discord.Color.red())
    embed.set_image(url=random.choice(gifler))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="zar_at", description="İstediğin yüzey sayısına sahip bir zar at.")
async def zar_at(interaction: discord.Interaction, yuzey: int = 6):
    gelen = random.randint(1, yuzey)
    await interaction.response.send_message(f"🎲 D{yuzey} Zarı atıldı... Gelen sayı: **{gelen}**")

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

@bot.tree.command(name="takimayarla", description="Kişileri rastgele takımlara böler.")
@app_commands.describe(takimsayi="Kaç adet takım oluşturulacak?", takimliste="İsimleri aralarına virgül (,) koyarak yazınız.")
async def takimayarla(interaction: discord.Interaction, takimsayi: int, takimliste: str):
    # 1. Listeyi virgüllerden ayırıp temizleyelim
    oyuncular = [isim.strip() for isim in takimliste.split(',') if isim.strip()]
    
    # 2. Hata Kontrolleri
    if takimsayi < 1:
        await interaction.response.send_message("❌ Takım sayısı en az 1 olmalıdır.", ephemeral=True)
        return
    
    if len(oyuncular) < takimsayi:
        await interaction.response.send_message(f"❌ Yeterli kişi yok! {len(oyuncular)} kişiyi {takimsayi} takıma bölemem.", ephemeral=True)
        return

    # 3. Listeyi Karıştır
    random.shuffle(oyuncular)

    # 4. Takımları Oluştur (Sözlük yapısı)
    takimlar = {i: [] for i in range(1, takimsayi + 1)}

    # 5. Oyuncuları sırayla takımlara dağıt
    for index, oyuncu in enumerate(oyuncular):
        takim_no = (index % takimsayi) + 1
        takimlar[takim_no].append(oyuncu)

    # 6. Embed Oluşturup Gönder
    embed = discord.Embed(
        title="🎲 Takımlar Oluşturuldu",
        description=f"Toplam **{len(oyuncular)}** kişi **{takimsayi}** takıma ayrıldı.",
        color=discord.Color.green()
    )

    for no, uyeler in takimlar.items():
        # Listeyi alt alta sırala
        uye_listesi = "\n".join([f"• {uye}" for uye in uyeler])
        embed.add_field(name=f"🏆 Takım {no}", value=uye_listesi, inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="anket", description="Basit bir anket başlatır.")
@app_commands.describe(soru="Anket sorusu nedir?")
async def anket(interaction: discord.Interaction, soru: str):
    embed = discord.Embed(
        title="📊 Yeni Anket!",
        description=f"**{soru}**",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"{interaction.user.display_name} tarafından başlatıldı.")
    
    # Mesajı gönderiyoruz ama bir değişkene atıyoruz ki tepki ekleyebilelim
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    
    # Evet/Hayır tepkilerini ekleyelim
    await message.add_reaction("✅")
    await message.add_reaction("❌")

@bot.tree.command(name="temizle", description="Belirtilen miktarda mesajı siler.")
@app_commands.describe(sayi="Silinecek mesaj sayısı")
@app_commands.checks.has_permissions(manage_messages=True) # Sadece yetkisi olanlar
async def temizle(interaction: discord.Interaction, sayi: int):
    if sayi > 100:
        await interaction.response.send_message("❌ Tek seferde en fazla 100 mesaj silebilirsin.", ephemeral=True)
        return

    # İşlem biraz sürebileceği için 'defer' kullanıyoruz (bekletiyor)
    await interaction.response.defer(ephemeral=True) 
    
    deleted = await interaction.channel.purge(limit=sayi)
    
    await interaction.followup.send(f"🧹 **{len(deleted)}** adet mesaj başarıyla silindi!", ephemeral=True)

# Yetki hatası olursa kullanıcıya bildirmek için hata yakalayıcı
@temizle.error
async def temizle_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bu komutu kullanmak için 'Mesajları Yönet' yetkisine sahip olmalısın Lordum.", ephemeral=True)

@bot.tree.command(name="avatar", description="Bir kullanıcının profil fotoğrafını büyük boy gösterir.")
@app_commands.describe(kullanici="Hangi kullanıcının avatarı?")
async def avatar(interaction: discord.Interaction, kullanici: discord.User):
    embed = discord.Embed(title=f"{kullanici.name} Avatarı", color=discord.Color.purple())
    embed.set_image(url=kullanici.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slot", description="Slot makinesini çevir!")
async def slot(interaction: discord.Interaction):
    emojiler = ["🍒", "🍋", "🍇", "🍉", "7️⃣", "💎"]
    a = random.choice(emojiler)
    b = random.choice(emojiler)
    c = random.choice(emojiler)

    slot_ekrani = f"**| {a} | {b} | {c} |**"
    
    if a == b == c:
        mesaj = f"🎉 **JACKPOT!** Tebrikler {interaction.user.mention}, büyük ödülü kazandın!"
        renk = discord.Color.gold()
    elif a == b or a == c or b == c:
        mesaj = f"🤏 **Ucu ucuna!** İki tane yakaladın, tekrar dene."
        renk = discord.Color.orange()
    else:
        mesaj = f"🥀 **Kaybettin.** Üzülme, kumarda kaybeden aşkta kazanır."
        renk = discord.Color.red()

    embed = discord.Embed(title="🎰 Slot Makinesi", description=f"{slot_ekrani}\n\n{mesaj}", color=renk)
    await interaction.response.send_message(embed=embed)

# --- DÜELLO SİSTEMİ İÇİN GEREKLİ SINIF ---

class DuelloView(discord.ui.View):
    def __init__(self, oyuncu1: discord.User, oyuncu2: discord.User):
        super().__init__(timeout=120) # 2 dakika süre aşımı
        self.p1 = oyuncu1
        self.p2 = oyuncu2
        self.hp = {self.p1.id: 100, self.p2.id: 100} # Başlangıç canları
        self.sira = self.p1.id # İlk sıra oyuncu 1'de
        self.log = "⚔️ Düello başladı! İlk hamle bekleniyor..."

    async def guncelle(self, interaction: discord.Interaction, bitti_mi=False):
        # Can durumuna göre görsel bar oluşturma fonksiyonu
        def can_bari(can):
            dolu = int(can / 10)
            return "🟩" * dolu + "⬜" * (10 - dolu)

        durum_metni = (
            f"**{self.p1.name}:** {self.hp[self.p1.id]} HP\n{can_bari(self.hp[self.p1.id])}\n\n"
            f"**{self.p2.name}:** {self.hp[self.p2.id]} HP\n{can_bari(self.hp[self.p2.id])}"
        )

        embed = discord.Embed(
            title="⚔️ DÜELLO ARENASI ⚔️",
            description=f"{durum_metni}\n\n📜 **Son Olay:**\n{self.log}",
            color=discord.Color.dark_red() if not bitti_mi else discord.Color.gold()
        )
        
        if not bitti_mi:
            siradaki = self.p1 if self.sira == self.p1.id else self.p2
            embed.set_footer(text=f"Sıra sende: {siradaki.name}", icon_url=siradaki.avatar.url if siradaki.avatar else None)
        else:
            embed.set_footer(text="Oyun Sona Erdi.")

        # Eğer oyun bittiyse butonları devre dışı bırak
        if bitti_mi:
            for child in self.children:
                child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def sira_kontrol(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.sira:
            await interaction.response.send_message(f"✋ Sıranı bekle {interaction.user.mention}!", ephemeral=True)
            return False
        return True

    async def sira_degis(self):
        self.sira = self.p2.id if self.sira == self.p1.id else self.p1.id

    # --- BUTONLAR ---

    @discord.ui.button(label="Saldır (Güvenli)", style=discord.ButtonStyle.primary, emoji="🗡️")
    async def normal_saldiri(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.sira_kontrol(interaction): return
        
        hasar = random.randint(10, 20)
        rakip_id = self.p2.id if self.sira == self.p1.id else self.p1.id
        self.hp[rakip_id] -= hasar
        
        vuran = self.p1.name if self.sira == self.p1.id else self.p2.name
        
        self.log = f"💥 **{vuran}**, rakibine **{hasar}** hasar vurdu!"
        
        if self.hp[rakip_id] <= 0:
            self.hp[rakip_id] = 0
            self.log = f"🏆 **{vuran}** KAZANDI! Rakibini yere serdi!"
            await self.guncelle(interaction, bitti_mi=True)
        else:
            await self.sira_degis()
            await self.guncelle(interaction)

    @discord.ui.button(label="Ağır Saldır (Riskli)", style=discord.ButtonStyle.danger, emoji="🪓")
    async def agir_saldiri(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.sira_kontrol(interaction): return

        # %40 ıska geçme şansı, ama vurursa çok vurur
        sans = random.randint(1, 100)
        vuran = self.p1.name if self.sira == self.p1.id else self.p2.name
        rakip_id = self.p2.id if self.sira == self.p1.id else self.p1.id

        if sans <= 40: # Iska
            self.log = f"💨 **{vuran}** ağır saldırı denedi ama ISKALADI!"
        else:
            hasar = random.randint(25, 40)
            self.hp[rakip_id] -= hasar
            self.log = f"🔥 **KRİTİK!** {vuran} balyoz gibi indirdi: **{hasar}** hasar!"

        if self.hp[rakip_id] <= 0:
            self.hp[rakip_id] = 0
            self.log = f"🏆 **{vuran}** risk aldı ve KAZANDI!"
            await self.guncelle(interaction, bitti_mi=True)
        else:
            await self.sira_degis()
            await self.guncelle(interaction)

    @discord.ui.button(label="İyileş", style=discord.ButtonStyle.success, emoji="🧪")
    async def iyiles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.sira_kontrol(interaction): return

        sifa = random.randint(10, 25)
        self.hp[self.sira] += sifa
        if self.hp[self.sira] > 100: self.hp[self.sira] = 100
        
        iyilesen = self.p1.name if self.sira == self.p1.id else self.p2.name
        self.log = f"✨ **{iyilesen}** iksir içti ve **{sifa}** can yeniledi."
        
        await self.sira_degis()
        await self.guncelle(interaction)

# --- KOMUT KISMI ---

@bot.tree.command(name="duello", description="Bir kullanıcı ile sıra tabanlı düello yap.")
@app_commands.describe(rakip="Kime meydan okuyorsun?")
async def duello(interaction: discord.Interaction, rakip: discord.User):
    if rakip.id == interaction.user.id:
        await interaction.response.send_message("❌ Kendinle dövüşemezsin Lordum, bu delilik olur!", ephemeral=True)
        return
    
    if rakip.bot:
        await interaction.response.send_message("🤖 Botlara gücün yetmez, insanlarla dövüş.", ephemeral=True)
        return

    view = DuelloView(interaction.user, rakip)
    
    embed = discord.Embed(
        title="⚔️ DÜELLO BAŞLIYOR ⚔️",
        description=f"{interaction.user.mention} 🆚 {rakip.mention}\n\nHer iki tarafın da **100 Canı** var.\nİlk hamleyi {interaction.user.mention} yapacak.",
        color=discord.Color.red()
    )
    
    await interaction.response.send_message(embed=embed, view=view)

# --- YARDIM MENÜSÜ ---

# ==========================================
# 5. YENİLENMİŞ YARDIM MENÜSÜ
# ==========================================

@bot.tree.command(name="komutlar", description="Tüm komutları kategorize edilmiş şekilde listeler.")
async def komutlar(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Bot Komut Merkezi",
        description=f"Lordum {interaction.user.mention}, emrinize amade toplam **30+** komut bulunmaktadır.",
        color=discord.Color.gold()
    )

    # 🛡️ Moderasyon
    embed.add_field(
        name="🛡️ Moderasyon & Yönetim",
        value="`/at`, `/yasakla`, `/yasak_kaldir`, `/timeout`, `/timeout_kaldir`, `/kanal_kilitle`, `/kanal_ac`, `/rol_ver`, `/rol_al`, `/temizle`",
        inline=False
    )

    # 📊 Bilgi & Analiz
    embed.add_field(
        name="📊 Bilgi & Analiz",
        value="`/sunucu_bilgi`, `/kullanici_bilgi`, `/avatar`, `/whoami`, `/ping`, `/rehber`",
        inline=False
    )

    # 🛠️ Araçlar
    embed.add_field(
        name="🛠️ Faydalı Araçlar",
        value="`/sifre_uret`, `/matematik`, `/kelime_say`, `/yaz` (Bot olarak yaz), `/anket`, `/takimayarla`, `/secim_yap`",
        inline=False
    )

    # 🎉 Eğlence
    embed.add_field(
        name="🎉 Eğlence & Oyun",
        value="`/duello`, `/slot`, `/8ball` (Sihirli Küre), `/ask_olc`, `/tas_kagit_makas`, `/zar_at`, `/tokat`, `/iltifat`, `/ters_yazi`, `/yazi_tura`, `/sansli_sayi`, `/saril`",
        inline=False
    )

    embed.set_footer(text="Furkan Otuk Hazretleri'nin hizmetindedir.", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    if not TOKEN:
        print("Hata: DISCORD_TOKEN bulunamadı! Coolify Environment kısmını kontrol et.")
    else:
        bot.run(TOKEN)