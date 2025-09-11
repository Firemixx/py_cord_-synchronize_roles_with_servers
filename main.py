import discord
import os # default module
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord import Member
from discord.utils import get
import logging
from log_config import configurated_logging


log=logging.getLogger()
load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.members = True
intents.guilds = True           
intents.presences = False  #разрешения, из-за которых я угробил четыре часаааа...
bot = commands.Bot(intents=intents)

guildlist_raw = os.getenv("guilds")
guildslist = list(map(int, guildlist_raw.split(",")))
endedOrNote=True


async def sync_roles():
    await configurated_logging(level=logging.INFO)
    log.info("Старт проверки и синхронизации")
    guilds = [bot.get_guild(g) for g in guildslist if bot.get_guild(g)]
    endedOrNote=False
    for guild in guilds:
        for member in guild.members:
            log.info(f"Чекинг {member.name} на {guild.name}")
            if member.bot:
                continue
                
            memberRoles=member.roles
            for r in memberRoles:
                rname=r.name
                log.info(f'имя пользователя:{rname}')
                if rname!='падаван':
                    log.warning(f'Имя роли что была пропущена:{r}')
                    continue
                if rname=='падаван':
                    for g in guilds:
                        
                        user=g.get_member(member.id)
                        # Цикл по всем серверам и передача ролей на них
                        role = discord.utils.get(g.roles, name=rname)
                        log.warning(f'Готовая роль для назначения:{role}')
                        if role:
                            try:
                                await user.add_roles(role)
                                log.info(f"{user.name} получил {rname} на сервере: {guild.name}")
                            except discord.Forbidden:
                                log.error(f"Нет прав выдать {rname} на {guild.name}")
                            else:
                                if role == None:
                                    log.fatal(f"{rname} нет на сервере {guild.name}")
    endedOrNote=True

@bot.event
async def on_ready():
    await configurated_logging(level=logging.INFO)
    log.info(f"{bot.user} запущен!")
    await sync_roles()  # Синхронизация


if endedOrNote==True:
    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        await configurated_logging(level=logging.INFO)
        guilds = [bot.get_guild(g) for g in guildslist if bot.get_guild(g)]
        memberRoles=after.roles
        for role in memberRoles:
            rname=role.name
            if rname=='падаван':
                for g in guilds:
                    log.info(f'Сервер:{g}')
                    log.info(f'Имя роли:{rname}')
                    user=g.get_member(after.id)
                    targetrole = discord.utils.get(g.roles , name=rname)
                    print(targetrole)
                    if targetrole:
                        try:
                            await user.add_roles(targetrole)
                            log.info(f'{user} получил роль:{targetrole.name}')
                        except discord.Forbidden:
                            log.error(f"Нет прав выдать {targetrole.name}")
                        else:
                            if targetrole == None:
                                log.fatal(f"{rname} нет на сервере")


#Выдать роли на всех сервах по названию
@bot.slash_command(description="give a role with synchronyzinc to other servers")
@discord.ext.commands.has_permissions(manage_messages=True)
async def set_role(ctx,user: discord.Member , * , rolename):
    await configurated_logging(level=logging.INFO)
    guildslist=os.getenv('guilds')
    for server in guildslist:
        targetguild = bot.get_guild(server)
        log.info(f'Сервер на котором проходит операция:{server}')
        targetrole = discord.utils.get(targetguild.roles , name=rolename)
        targetmember = targetguild.get_member(user.id)
        await targetmember.add_roles(targetrole)
        log.info(f'Бот успешно выдал роль {targetrole}, на серверах {guildslist} пользователю {targetmember}')
        await ctx.response.send_message(f"Бот {bot.user} совершил попытку изменить роль {targetmember}-у на {targetrole} на серверах {guildslist}",ephemeral=True)

#Лишить роли на всех сервах по названию 
@bot.slash_command(description="remove a role with synchronyzinc to other servers")
@discord.ext.commands.has_permissions(manage_messages=True)
async def remove_role(ctx,user: discord.Member , * , rolename):
    await configurated_logging(level=logging.INFO)
    for server in guildslist:
        targetguild = bot.get_guild(server)
        log.info(f'Сервер на котором проходит операция:{server}')
        targetrole = discord.utils.get(targetguild.roles , name=rolename)
        targetmember = targetguild.get_member(user.id)
        await targetmember.remove_roles(targetrole)
    log.info(f'Бот успешно удалил роль {targetrole}, на серверах {guildslist} пользователю {targetmember}')
    await ctx.response.send_message(f"Бот {bot.user} совершил попытку удалить роль у {targetmember} на сервере {guildslist}",ephemeral=True)

bot.run(os.getenv('TOKEN')) # run the bot with the token