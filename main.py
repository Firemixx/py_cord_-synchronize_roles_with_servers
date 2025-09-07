import discord
import os # default module
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord import Member
from discord.utils import get

load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.members = True
intents.guilds = True           
intents.presences = False  #Intests for what I waste 4 hourssss...
bot = commands.Bot(intents=intents)


guildslist=[]#Servers on what will work bot
lenofGlist=len(guildslist)


@bot.event
async def on_ready():
    print(f"{bot.user} запущен!")
    sync_roles.start()  # synchronize


@tasks.loop(seconds=15)
async def sync_roles():
    print("Старт проверки и синхронизации")

    guilds = [bot.get_guild(g) for g in guildslist if bot.get_guild(g)]

    for guild in guilds:
        for member in guild.members:
            print(f"Чекинг {member.name} на {guild.name}")
            for r in member.roles:
                print(f"   - {r.name}")
            if member.bot:
                continue

            # Taking ALL roles from servers
            user_roles_names = set()
            for g in guilds:
                m = g.get_member(member.id)
                if not m:
                    continue
                for r in m.roles:
                    if r.name not in ["@everyone", "BotRole"]:#trash roles are going from list of roles on synchronize
                        user_roles_names.add(r.name)


            # Cicle for all servers on list and adding roles
            for g in guilds:
                target_member = g.get_member(member.id)
                if not target_member:
                    continue

                current_roles = [r.name for r in target_member.roles]

                for role_name in user_roles_names:
                    if role_name not in current_roles:
                        role = discord.utils.get(g.roles, name=role_name)
                        if role:
                            try:
                                await target_member.add_roles(role)
                                print(f"{target_member.name} получил {role_name} на сервере: {g.name}")
                            except discord.Forbidden:
                                print(f"Нет прав выдать {role_name} на {g.name}")
                        else:
                            print(f"{role_name} нет на сервере {g.name}")

#Giving role with synchronize
@bot.slash_command(description="give a role with synchronyzinc to other servers")
@discord.ext.commands.has_permissions(manage_messages=True)
async def set_role(ctx,user: discord.Member , * , rolename):
    for server in guildslist:
        targetguild = bot.get_guild(server)
        print(server)
        targetrole = discord.utils.get(targetguild.roles , name=rolename)
        targetmember = targetguild.get_member(user.id)
        await targetmember.add_roles(targetrole)
        await ctx.response.send_message(f"Бот {bot.user} совершил попытку изменить роль {targetmember}-у на {targetrole} на серверах {guildslist}",ephemeral=True)

#Remove role with synchronize
@bot.slash_command(description="remove a role with synchronyzinc to other servers")
@discord.ext.commands.has_permissions(manage_messages=True)
async def remove_role(ctx,user: discord.Member , * , rolename):
    for server in guildslist:
        targetguild = bot.get_guild(server)
        print(server)
        targetrole = discord.utils.get(targetguild.roles , name=rolename)
        targetmember = targetguild.get_member(user.id)
        await targetmember.remove_roles(targetrole)
    await ctx.response.send_message(f"Бот {bot.user} совершил попытку удалить роль у {targetmember} на сервере {guildslist}",ephemeral=True)

bot.run(os.getenv('TOKEN')) # run the bot with the token














#synchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronizesynchronize....i hate this word