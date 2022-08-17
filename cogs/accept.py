from email.policy import default
import discord
from discord.ext import commands

from main import MainCli


class Accept(commands.Cog, name='Accept'):
    def __init__(self, client: MainCli) -> None:
        self.client = client

    @commands.command(
        name='accept',
        description='Accepts an invite',
        pass_context=True
    )
    async def accept(self, context: commands.Context, member: discord.Member) -> None:
        mem_is_admin = False

        for role in context.author.roles:
            if role.permissions.administrator:
                mem_is_admin = True

                break

        if context.author == context.author.guild.owner:
            mem_is_admin = True

        if not mem_is_admin:
            return await context.send(
                'You must be an administrator to use this command.'
            )  
        
        for role in member.roles:
            try:
                await member.remove_roles(role)
            except Exception as e:
                print(e)

        default_role = await self.client.roles_db.get_role(context.guild.id)
        
        role = discord.utils.get(context.guild.roles, id=default_role)

        if role:
            await member.add_roles(role)
        
        await context.send(f'{member.name} has been accepted')

        await member.send(
            content=(
                f"Вашу заявку принял администратор {context.author.mention}!\n\n"
                "Веди себя адекватно, и не будь долбаёбом."
            )
        )

    @commands.command(
        name='decline',
        description='Declines an invite',
        pass_context=True
    )
    async def decline(self, context: commands.Context, member: discord.Member) -> None:
        mem_is_admin = False

        for role in context.author.roles:
            if role.permissions.administrator:
                mem_is_admin = True

                break

        if context.author == context.author.guild.owner:
            mem_is_admin = True

        if not mem_is_admin:
            return await context.send(
                'You must be an administrator to use this command.'
            )  
        
        await context.send(f'{member.name} has been declined')

        await member.send(
            content=(
                f"Вашу заявку отклонил администратор {context.author.mention}!\n\n"
            )
        )

        await member.kick(reason='Declined by an administrator')


def setup(client: MainCli) -> None:
    client.add_cog(Accept(client))
