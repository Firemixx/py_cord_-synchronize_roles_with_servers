import discord
import os # default module
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord import Member
from discord.utils import get
import logging,asyncio
from log_config import configurated_logging

log=logging.getLogger()
load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.members = True
intents.guilds = True           
intents.presences = True  #разрешения, из-за которых я угробил четыре часаааа...
bot = commands.Bot(intents=intents)

guildlist_raw = os.getenv("guilds")
guildslist = list(map(int, guildlist_raw.split(",")))
guildlistAndRoles_raw = os.getenv("guildsRolesPadavan")
guildlistAndRoles = {
    int(server_id): [int(rid) for rid in role_ids.strip("()").split(";")]
    for server_id, role_ids in (pair.split(":") for pair in guildlistAndRoles_raw.split(",") if pair)
}

async def sync_roles():
    await configurated_logging(level=logging.INFO)
    log.info("Старт проверки и синхронизации")
    guilds = [bot.get_guild(g) for g in guildslist if bot.get_guild(g)]
    for guild in guilds:
        for r in guildlistAndRoles[guild.id]:
            role=discord.utils.get(guild.roles,id=r)
            for member in role.members:
                if member.bot:
                    continue
                member_role_ids = [r.id for r in member.roles]
                tasks = []
                for r_id in member_role_ids:
                    if r_id not in guildlistAndRoles[guild.id]:
                        continue
                    idx = guildlistAndRoles[guild.id].index(r_id)
                    for target_guild_id, role_list in guildlistAndRoles.items():
                        target_guild = bot.get_guild(target_guild_id)
                        if not target_guild:
                            continue
                        if idx >= len(role_list):
                            continue
                        target_role_id = role_list[idx]
                        target_member = target_guild.get_member(member.id)
                        if not target_member:
                            continue
                        target_role = target_guild.get_role(target_role_id)
                        if not target_role:
                            continue
                        if all(r.id != target_role.id for r in target_member.roles):
                            tasks.append(target_member.add_roles(target_role, reason="Синхронизация ролей"))

                if tasks:
                    try:
                        await asyncio.gather(*tasks)
                        log.info(f"Синхронизация:{member.name} получил новые роли на сервер(ах).")
                    except discord.Forbidden:
                        log.error("Синхронизация:Нет прав выдать одну из ролей")
                log.info('Синхронизация:Прошла успешно')


@bot.event
async def on_ready():
    await configurated_logging(level=logging.INFO)
    log.info(f"{bot.user} запущен!")
    await sync_roles()  # Синхронизация

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await configurated_logging(level=logging.INFO)
    tasks = []
    aroles=after.roles
    for ar in aroles:
        if ar.id not in guildlistAndRoles[after.guild.id]:
            continue
        idx = guildlistAndRoles[after.guild.id].index(ar.id)
        for target_guild_id, role_list in guildlistAndRoles.items():
            target_guild = bot.get_guild(target_guild_id)
            if not target_guild:
                continue
            if idx >= len(role_list):
                continue
            target_role_id = role_list[idx]
            target_member = target_guild.get_member(after.id)
            if not target_member:
                continue
            target_role = target_guild.get_role(target_role_id)
            if not target_role:
                continue
            if all(r.id != target_role.id for r in target_member.roles):
                tasks.append(target_member.add_roles(target_role, reason="Синхронизация ролей при изменении"))

        if tasks:
            try:
                await asyncio.gather(*tasks)
                log.info(f"Синхронизация при изменении:{after.name} получил новые роли на серверах из списка.")
            except discord.Forbidden:
                log.error("Синхронизация при изменении:Нет прав выдать одну из ролей")

bot.run(os.getenv('TOKEN')) # run the bot with the token