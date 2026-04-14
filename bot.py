import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os
import re
from flask import Flask
from threading import Thread

# Flask สำหรับ keep alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web, daemon=True).start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def detect_lang(text):
    if re.search(r'[\u0E00-\u0E7F]', text):
        return 'th'
    return 'en'

@bot.command(name='tts')
async def tts(ctx, *, text: str):
    if not ctx.author.voice:
        await ctx.send("❌ กรุณาเข้า Voice Channel ก่อนนะ!")
        return

    voice_channel = ctx.author.voice.channel
    print(f"[TTS] คำสั่งจาก {ctx.author} ข้อความ: {text}")

    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    else:
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=True)
        vc = await voice_channel.connect()

    await asyncio.sleep(1)

    if not vc.is_connected():
        await ctx.send("❌ เชื่อมต่อ Voice Channel ไม่สำเร็จ")
        return

    print(f"[TTS] เชื่อมต่อ Voice Channel สำเร็จ")

    lang = detect_lang(text)
    tts_obj = gTTS(text=text, lang=lang, slow=False)
    filename = f'tts_{ctx.message.id}.mp3'
    tts_obj.save(filename)
    print(f"[TTS] สร้างไฟล์เสียงสำเร็จ: {filename} ภาษา: {lang}")

    await ctx.message.add_reaction('🔊')

    def after_play(error):
        if error:
            print(f"[TTS] เกิด error ตอนเล่น: {error}")
        else:
            print(f"[TTS] เล่นเสียงเสร็จแล้ว")
        if os.path.exists(filename):
            os.remove(filename)
        asyncio.run_coroutine_threadsafe(
            ctx.message.add_reaction('✅'), bot.loop
        )

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
