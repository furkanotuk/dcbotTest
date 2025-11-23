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

@bot.tree.command(name="komutlar", description="Mevcut tüm komutları ve kullanımlarını listeler.")
async def komutlar(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Komut Listesi",
        description="Bot üzerinde kullanabileceğin tüm komutlar ve detayları aşağıdadır Lordum:",
        color=discord.Color.gold()
    )

    # Genel Komutlar
    embed.add_field(
        name="⚙️ Genel & Sistem",
        value=(
            "**/rehber** - Hosting ve kurulum rehberini gösterir.\n"
            "**/ping** - Botun gecikme süresini (ms) gösterir.\n"
            "**/whoami** - Bot hakkında genel bilgi verir."
        ),
        inline=False
    )

    # Eğlence Komutları
    embed.add_field(
        name="🎉 Eğlence & Oyun",
        value=(
            "**/duello [kullanıcı]** - Etiketlediğin kişiyle sıra tabanlı bir savaşa girersin.\n"
            "**/slot** - Şansını slot makinesinde denersin.\n"
            "**/yazi_tura** - Havaya para atar.\n"
            "**/sansli_sayi** - Sana özel 0-100 arası bir sayı üretir.\n"
            "**/saril [kullanıcı]** - Birine sanal olarak sarılırsın."
        ),
        inline=False
    )

    # Araçlar ve Moderasyon
    embed.add_field(
        name="🛠️ Araçlar & Yönetim",
        value=(
            "**/takimayarla [sayı] [isimler]** - İsimleri virgülle ayırarak yaz, rastgele takımlara böler.\n"
            "**/secim_yap [seçenek1] [seçenek2]** - İki arada kaldıysan senin yerine seçer.\n"
            "**/anket [soru]** - Evet/Hayır tepkili bir anket başlatır.\n"
            "**/avatar [kullanıcı]** - Kullanıcının profil resmini büyütür.\n"
            "**/temizle [sayı]** - Belirtilen sayıda mesajı siler (Yetki gerektirir)."
        ),
        inline=False
    )

    embed.set_footer(text=f"{bot.user.name} hizmetinizde.", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    if not TOKEN:
        print("Hata: DISCORD_TOKEN bulunamadı! Coolify Environment kısmını kontrol et.")
    else:
        bot.run(TOKEN)