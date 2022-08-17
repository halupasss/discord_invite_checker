import asyncio
import discord
from discord.ext import commands

from main import MainCli


class OnConnect(commands.Cog):
    def __init__(self, client: MainCli):
        self.client = client

        self.client.add_listener(on_connect, 'on_connect')


async def on_connect() -> None:
    await _client.load_databases()


def setup(client: MainCli) -> None:
    global _client

    _client = client

    client.add_cog(OnConnect(client))
