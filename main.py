from http import client
import os
import asyncio
import logging
import platform

import asyncpg
import discord
from discord.ext import commands

from databases.invites_db import InvitesSettingsDataBase, InvitesDataBase, StartRolesDataBase

COMMAND_PREFIX = 'do '
TOKEN = ''
POSTGRES_PASSWORD = ''

logging.basicConfig(level=logging.INFO)


class MainCli(commands.Bot):
    invites_settings_db: InvitesSettingsDataBase
    invites_db: InvitesDataBase
    roles_db: StartRolesDataBase

    def __init__(self):
        super().__init__(
            command_prefix='do ',
            case_insensitive=False,
            intents=discord.Intents.all()
        )

    async def print_load_info(self) -> None:
        logging.info(f"Discord.py API version: {discord.__version__}")
        logging.info(f"Python version: {platform.python_version()}")
        logging.info(f"Launched on: {platform.system()} {platform.release()} ({os.name})")
        logging.info(f'command prefix is: \'{COMMAND_PREFIX}\'')

    async def load_event_handlers(self) -> None:
        try:
            for file in os.listdir("./events"):
                if file.endswith(".py"):
                    file_name = file[:-3]
                    try:
                        self.load_extension(f"events.{file_name}")

                        logging.info(f"Event handler loaded: '{file_name}'")
                    except Exception as error:
                        exception = f"{type(error).__name__}: {error}"

                        logging.info(f"Failed to load event handler: {file_name}\n{exception}")

        except Exception as error:
            logging.error(error)

    async def load_cogs(self) -> None:
        try:
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    file_name = file[:-3]
                    try:
                        self.load_extension(f"cogs.{file_name}")

                        logging.info(f"Module loaded: '{file_name}'")
                    except Exception as error:
                        exception = f"{type(error).__name__}: {error}"

                        logging.error(f"Failed to load module: {file_name}\n{exception}")

        except Exception as error:
            logging.error(error)

    async def load_databases(self) -> None:
        pool = await asyncpg.create_pool(
            user='postgres',
            password=POSTGRES_PASSWORD,
            database='postgres',
            host='127.0.0.1',
            port=5432,
            max_inactive_connection_lifetime=3
        )

        logging.info('Connected to database')

        self.invites_settings_db = InvitesSettingsDataBase(pool)
        self.invites_db = InvitesDataBase(pool)
        self.roles_db = StartRolesDataBase(pool)

    async def load(self) -> None:
        await self.print_load_info()
        await self.load_event_handlers()
        await self.load_cogs()


def main() -> None:
    cli = MainCli()

    asyncio.run(cli.load())

    cli.run(TOKEN)


if __name__ == '__main__':
    main()    
