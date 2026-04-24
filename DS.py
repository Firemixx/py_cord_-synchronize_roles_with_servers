import discord
import os
from discord.ext import tasks
from discord.ext.commands import has_permissions
from discord import Member
from discord.utils import get
import logging
import asyncio
from log_config import configurated_logging
from dotenv import load_dotenv

load_dotenv()


class RoleSyncManager:

    def __init__(self,bot:discord.Client):
        self.bot=bot
        self.guilds=self.bot.guilds


    async def start_sync(self):
        guilds = self.guilds
        role_map = {}
        for g in guilds:
            for r in g.roles:
                role_map.setdefault(r.name, {})[g.id] = r
        sets = [{m.id for m in g.members} for g in guilds]
        all_users = set.union(*sets)
        for user_id in all_users:
            user_roles = set()
            members = {}
            for g in guilds:
                m = g.get_member(user_id)
                if not m:
                    continue
                members[g.id] = m
                user_roles.update(r.name for r in m.roles if not r.is_default())
            for role_name in user_roles:
                guild_roles = role_map.get(role_name, {})
                for g in guilds:
                    m = members.get(g.id)
                    role = guild_roles.get(g.id)
                    if not m or not role:
                        continue
                    if role not in m.roles:
                        await m.add_roles(role)

    async def on_member_update(self,before:Member,after:Member):
        if before.roles!=after.roles:
            if len(before.roles)>len(after.roles):
                delete=True
            else:
                delete=False
            id=after.id
            delete=set(before.roles)-set(after.roles)
            add=set(after.roles)-set(before.roles)
            if delete:
                names_roles=[i.name for i in delete]
            else:
                names_roles=[i.name for i in add]
            for g in self.guilds:
                member=g.get_member(id)
                for i in names_roles:
                    role=discord.utils.get(g.roles, name=i)
                    if delete:
                        await member.remove_roles(role)
                    else:
                        await member.add_roles(role)

    async def on_member_join(self,member:discord.Member):
        user_id=member.id
        user_roles_name=[]
        for g in self.guilds:
            if g is member.guild:
                continue
            user_other_guild=g.get_member(user_id)
            user_roles_name=[r.name for r in user_other_guild.roles]
        user_guild_roles=member.guild.roles
        user_guild_roles_name=[r.name for r in user_guild_roles]
        common_roles_name=set(user_roles_name)&set(user_guild_roles_name)
        for r in common_roles_name:
            role=discord.utils.get(member.guild.roles, name=r)
            await member.add_roles(role)
