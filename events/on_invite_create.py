import discord
from discord.ext import commands

from main import MainCli


class OnInviteCreate(commands.Cog):
    def __init__(self, client: MainCli):
        self.client = client

        self.client.add_listener(on_invite_create, 'on_invite_create')


async def check_invite(invite: discord.Invite) -> None:
    '''
    removes an invite if the number of uses is more than one

    @param invite: discord.Invite

    @return: None
    '''

    limit = await _client.invites_settings_db.get_invite_limit(invite.guild.id)

    if invite.max_uses > limit:
        return await invite.delete(reason='invite used more than limit')

    await _client.invites_db.add_invite(invite.code, invite.inviter.id)


async def on_invite_create(invite: discord.Invite) -> None:
    await check_invite(invite)


def setup(client: MainCli) -> None:
    global _client

    _client = client

    client.add_cog(OnInviteCreate(client))
