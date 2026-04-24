import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import logging
import asyncio
from log_config import configurated_logging
import DS as ds
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


log=logging.getLogger()
load_dotenv()
intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    dsSyncr=ds.RoleSyncManager(bot=bot)
    await dsSyncr.start_sync()

@bot.event
async def on_member_update(before,after):
    dsSyncr=ds.RoleSyncManager(bot=bot)
    await dsSyncr.on_member_update(before,after)

@bot.event
async def on_member_join(member):
    dsSyncr=ds.RoleSyncManager(bot=bot)
    await dsSyncr.on_member_join(member)

bot.run(os.getenv('TOKEN'))