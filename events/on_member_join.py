import discord
import datetime
from discord.ext import commands

from main import MainCli

CREATOR_ID = 553284071380484129


class OnMemberJoin(commands.Cog):
    def __init__(self, client: MainCli) -> None:
        self.client = client

        self.client.add_listener(on_member_join, 'on_member_join')


async def get_previous_invite_state(guild: discord.Guild) -> list[discord.Invite]:
    '''
    get the previous invite state for the guild

    @param guild: discord.Guild

    @return: bool
    '''

    prev_state = []

    for invite in await guild.invites():
        invite_info = await _client.invites_db.get_invite(invite.code)

        prev_state.append(invite_info)

    return prev_state


async def find_invite_author(new_member: discord.Member) -> discord.Member:
    '''
    find the creator of the invite

    @param new_member: discord.Member

    @return: discord.Member
    '''
    
    prev_state = await get_previous_invite_state(new_member.guild)

    for invite_info in prev_state:
        guild: discord.Guild = new_member.guild

        guild_invites = await guild.invites()

        for invite in guild_invites:
            invite: discord.Invite

            if (invite.uses - 1) == invite_info.uses:
                await _client.invites_db.add_uses(invite.code)

                return invite.inviter

    return None


async def send_member_info(member: discord.Member, refferal: str) -> None:
    '''
    Выводит всю информацию о новом пользователе

    @param1: member discord.Member

    @return: None
    '''

    channel_id = await _client.invites_settings_db.get_channel(member.guild.id)

    channel: discord.TextChannel = discord.utils.get(member.guild.channels, id=channel_id)

    if not channel:
        return

    date_format = "%d.%m.%Y %I:%M %p"

    guild: discord.Guild = member.guild

    icon_url = None

    if guild.icon:
        try:
            icon_url = guild.icon.url
        except Exception as e:
            print(e)
    else:
        icon_url = guild.owner.avatar.url

    message_embed = (
        discord.Embed(
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now()
        )
        .set_footer(
            text=f"new member: {member.name}#{member.discriminator}",
            icon_url=icon_url
        )
        .set_thumbnail(
            url=member.avatar.url
        )
        .add_field(
            name='member',
            value=member.mention,
            inline=True
        )
        .add_field(
            name='refferal',
            value=refferal,
            inline=True
        )
        .add_field(
            name='created at',
            value=member.created_at.strftime(date_format),
            inline=False
        )
        .add_field(
            name='joined at',
            value=member.joined_at.strftime(date_format),
            inline=False
        )
        .add_field(
            name='member id',
            value=member.id,
            inline=False
        )
    )

    await channel.send(embed=message_embed)


async def send_hello_msg(member: discord.Member) -> None:
    await member.send(
        content=(
            f"Добро пожаловать на сервер {member.guild}!\n\n"
            "Пока что ваш аккаунт не активирован, для получения доступа дождитесь пока администраторы активируют ваш аккаунт.\n⠀"
        )
    )


async def on_member_join(member: discord.Member) -> None:
    if not member:
        return
    
    await send_hello_msg(member)

    author = await find_invite_author(member) or 'Unknown'

    channel_id = await _client.invites_settings_db.get_channel(member.guild.id)

    channel = discord.utils.get(member.guild.channels, id=channel_id)

    administrators = ''

    for member in member.guild.members:
        member: discord.Member

        is_admin = False
        is_bot = False

        for role in member.roles:
            role: discord.Role

            if role.is_bot_managed():
                is_bot = True

            if role.permissions.administrator and (member != member.guild.owner):
                is_admin = True

        if is_admin and (not is_bot):
            administrators += member.mention + ' '

    administrators += member.guild.owner.mention

    message_embed = (
        discord.Embed(
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
            description=f'write `do accept {member.id}` to add it'
        )
        .add_field(
            name='who can accept',
            value=administrators,
            inline=False
        )
    )

    if author != 'Unknown':
        author = author.mention

    if channel:
        await send_member_info(member, author)

        await channel.send(
            embed=message_embed
        )

    guild: discord.Guild = member.guild
    invites: list[discord.Invite] = await guild.invites()

    for invite in invites:
        invite: discord.Invite

        invite_limit = await _client.invites_settings_db.get_invite_limit(guild.id)

        if invite.uses >= invite_limit:
            await invite.delete(reason='invite limit reached')


def setup(client: MainCli) -> None:
    global _client

    _client = client

    client.add_cog(OnMemberJoin(client))
