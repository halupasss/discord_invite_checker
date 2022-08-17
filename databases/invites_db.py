import asyncpg


class InvitesSettings:
    guild_id: int
    channel_id: int
    invite_limit: int

    def __init__(self, guild_id: int, invite_limit: int, channel_id: int):
        self.guild_id = guild_id

        if channel_id != -1:
            self.channel_id = channel_id

        if invite_limit != -1:
            self.invite_limit = invite_limit


class Invite:
    code: str
    author_id: int
    uses: int

    def __init__(self, code: str, author_id: int=-1, uses: int=-1):
        self.code = code

        if uses != -1:
            self.uses = uses

        if author_id != -1:
            self.author_id = author_id

    def __repr__(self):
        return f'Invite({self.code}, {self.author_id}, {self.uses})'
        

class InvitesSettingsDataBase:
    CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS invites_settings (
            guild_id BIGINT PRIMARY KEY,
            invite_limit INTEGER,
            channel_id BIGINT
        )
    '''

    def __init__(self, pool):
        self.pool: asyncpg.pool.Pool = pool
        self.chache = {}

    async def update_chache(self, guild_id: int, invite_limit: int=-1, channel_id: int=-1) -> None:
        self.chache[guild_id] = InvitesSettings(guild_id, invite_limit, channel_id)

    async def set_invite_limit(self, guild_id: int, invite_limit: int) -> None:
        await self.update_chache(guild_id, invite_limit=invite_limit)

        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'INSERT INTO invites_settings (guild_id, invite_limit) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET invite_limit = $2',
                guild_id,
                invite_limit
            )

    async def get_invite_limit(self, guild_id: int) -> int:
        if guild_id in self.chache:
            return self.chache[guild_id].invite_limit

        async with self.pool.acquire() as conn:
            invite_limit = await conn.fetchval(
                'SELECT invite_limit FROM invites_settings WHERE guild_id = $1',
                guild_id
            )

            return invite_limit or 0

    async def set_channel(self, guild_id: int, channel_id: int) -> None:
        await self.update_chache(guild_id, channel_id=channel_id)

        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'INSERT INTO invites_settings (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2',
                guild_id,
                channel_id
            )
    
    async def get_channel(self, guild_id: int) -> int:
        async with self.pool.acquire() as conn:
            channel_id = await conn.fetchval(
                'SELECT channel_id FROM invites_settings WHERE guild_id = $1',
                guild_id
            )

            return channel_id

    def __del__(self):
        self.pool.close()


class InvitesDataBase:
    CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS invites (
            invite_id TEXT PRIMARY KEY,
            author_id BIGINT,
            uses INTEGER
        )
    '''
    def __init__(self, pool):
        self.pool: asyncpg.pool.Pool = pool
        self.chache = {}

    async def update_chache(self, invite_id: str, author_id: int, uses: int) -> None:
        self.chache[invite_id] = Invite(author_id, invite_id, uses)

    async def get_invite(self, invite_id: str) -> Invite:
        if invite_id in self.chache:
            return self.chache[invite_id]

        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)
            
            author_id = await conn.fetchval(
                'SELECT author_id FROM invites WHERE invite_id = $1',
                invite_id
            )

            uses = await conn.fetchval(
                'SELECT uses FROM invites WHERE invite_id = $1',
                invite_id
            )

            return Invite(invite_id, author_id, uses)

    async def add_invite(self, invite_id: str, author_id: int) -> None:
        await self.update_chache(invite_id, author_id, 0)

        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'INSERT INTO invites (invite_id, author_id) VALUES ($1, $2)',
                invite_id,
                author_id
            )

    async def add_uses(self, invite_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'UPDATE invites SET uses = uses + 1 WHERE invite_id = $1',
                invite_id
            )

    async def delete_invite(self, invite_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'DELETE FROM invites WHERE invite_id = $1',
                invite_id
            )

    def __del__(self):
        self.pool.close()


class StartRolesDataBase:
    CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS start_roles (
            guild_id BIGINT PRIMARY KEY,
            role_id BIGINT
        )
    '''

    def __init__(self, pool):
        self.pool: asyncpg.pool.Pool = pool
        self.chache = {}

    async def update_chache(self, guild_id: int, role_id: int) -> None:
        self.chache[guild_id] = role_id

    async def get_role(self, guild_id: int) -> int:
        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            role_id = await conn.fetchval(
                'SELECT role_id FROM start_roles WHERE guild_id = $1',
                guild_id
            )

            return role_id

    async def set_role(self, guild_id: int, role_id: int) -> None:
        await self.update_chache(guild_id, role_id)

        async with self.pool.acquire() as conn:
            await conn.execute(self.CREATE_TABLE)

            await conn.execute(
                'INSERT INTO start_roles (guild_id, role_id) VALUES ($1, $2)',
                guild_id,
                role_id
            )

    def __del__(self):
        self.pool.close()
