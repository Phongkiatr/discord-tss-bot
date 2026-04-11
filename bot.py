import discord
from discord.ext import commands
from gtts import gTTS
from flask import Flask
from threading import Thread
import asyncio
import os
import re

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def detect_lang(text):
    # ถ้ามีอักษรไทย → ภาษาไทย
    if re.search(r'[\u0E00-\u0E7F]', text):
        return 'th'
    return 'en'

@bot.command(name='tts')
async def tts(ctx, *, text: str):
    # ต้องอยู่ใน voice channel
    if not ctx.author.voice:
        await ctx.send("❌ กรุณาเข้า Voice Channel ก่อนนะ!")
        return

    voice_channel = ctx.author.voice.channel

    # เชื่อมต่อหรือย้าย voice channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    else:
        vc = await voice_channel.connect()

    # สร้างไฟล์เสียง
    lang = detect_lang(text)
    tts_obj = gTTS(text=text, lang=lang, slow=False)
    filename = f'tts_{ctx.message.id}.mp3'
    tts_obj.save(filename)

    await ctx.send(f"🔊 กำลังพูด: **{text}**")

    # เล่นเสียง
    def after_play(error):
        os.remove(filename)
        if len(vc.channel.members) == 1:  # เหลือแค่ bot
            asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)

    vc.play(
        discord.FFmpegPCMAudio(filename),
        after=after_play
    )

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกจาก Voice Channel แล้ว")

@bot.event
async def on_ready():
    print(f'✅ Bot พร้อมแล้ว: {bot.user}')

bot.run(os.environ['DISCORD_TOKEN'])

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web, daemon=True).start()
