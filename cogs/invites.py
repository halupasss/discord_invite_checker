import discord
from discord.ext import commands

from main import MainCli


class Invites(commands.Cog, name='invites'):
    def __init__(self, client: MainCli) -> None:
        self.client = client

    @commands.command(
        name='set_invite_limit',
        description='Sets the invite limit for the server',
        pass_context=True
    )
    async def set_invite_limit(self, context: commands.Context, limit: int) -> None:
        '''
        Sets the invite limit for the server

        @param context: discord.ext.commands.Context
        @param limit: int

        @return: None
        '''

        if limit < 0:
            return await context.send('Invalid limit')

        try:
            await self.client.invites_settings_db.set_invite_limit(context.guild.id, limit)

            await context.send(f'Invite limit set to `{limit}`')
        except discord.Forbidden:
            await context.send('I do not have permission to set the invite limit')

    @commands.command(
        name='get_invite_limit',
        description='Gets the invite limit for the server',
        pass_context=True
    )
    async def get_invite_limit(self, context: commands.Context) -> None:
        '''
        Gets the invite limit for the server

        @param context: discord.ext.commands.Context

        @return: None
        '''

        try:
            limit = await self.client.invites_settings_db.get_invite_limit(context.guild.id)

            await context.send(f'Invite limit is `{limit}`')
        except discord.Forbidden:
            await context.send('I do not have permission to get the invite limit')

    @commands.command(
        name='set_channel',
        description='Sets the channel for the server',
        pass_context=True
    )
    async def set_channel(self, context: commands.Context, channel: discord.TextChannel) -> None:
        '''
        Sets the channel for the server

        @param context: discord.ext.commands.Context
        @param channel: discord.TextChannel

        @return: None
        '''

        try:
            await self.client.invites_settings_db.set_channel(context.guild.id, channel.id)

            await context.send(f'Channel set to {channel.mention}')
        except discord.Forbidden:
            await context.send('I do not have permission to set the channel')

    @commands.command(
        name='get_channel',
        description='Gets the channel for the server',
        pass_context=True
    )
    async def get_channel(self, context: commands.Context) -> None:
        '''
        Gets the channel for the server

        @param context: discord.ext.commands.Context

        @return: None
        '''

        try:
            channel_id = await self.client.invites_settings_db.get_channel(context.guild.id)

            channel = discord.utils.get(context.guild.text_channels, id=channel_id)

            await context.send(f'Channel is {channel.mention}')
        except discord.Forbidden:
            await context.send('I do not have permission to get the channel')

    @commands.command(
        name='set_role',
        description='Sets the role for the server',
        pass_context=True
    )
    async def set_role(self, context: commands.Context, role: discord.Role) -> None:
        '''
        Sets the role for the server

        @param context: discord.ext.commands.Context
        @param role: discord.Role

        @return: None
        '''

        try:
            await self.client.roles_db.set_role(context.guild.id, role.id)

            await context.send(f'Role set to {role.mention}')
        except discord.Forbidden:
            await context.send('I do not have permission to set the role')

    @commands.command(
        name='get_role',
        description='Gets the role for the server',
        pass_context=True
    )
    async def get_role(self, context: commands.Context) -> None:
        '''
        Gets the role for the server

        @param context: discord.ext.commands.Context

        @return: None
        '''

        try:
            role_id = await self.client.roles_db.get_role(context.guild.id)

            role = discord.utils.get(context.guild.roles, id=role_id)

            await context.send(f'Role is {role.mention}')
        except discord.Forbidden:
            await context.send('I do not have permission to get the role')


def setup(client: MainCli) -> None:
    client.add_cog(Invites(client))
