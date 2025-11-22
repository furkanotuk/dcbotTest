import discord
import os
from discord.ext import commands

# Tokeni environment variable'dan çekiyoruz (Güvenlik için şart)
TOKEN = os.getenv('DISCORD_TOKEN')

# Intent ayarları (Discord Developer Portal'dan Message Content Intent açılmalı)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Bot Giriş Yaptı: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'------------------------------------')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Gecikme: {round(bot.latency * 1000)}ms 🚀')

@bot.command()
async def whoami(ctx):
    await ctx.send(f'🚀 Merhaba ! Ben Genelsoft sunucusu üzerinde barındırılan bir Discord botuyum.')

if __name__ == "__main__":
    if not TOKEN:
        print("Hata: DISCORD_TOKEN bulunamadı! Coolify Environment kısmını kontrol et.")
    else:
        bot.run(TOKEN)