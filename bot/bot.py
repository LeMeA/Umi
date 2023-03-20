from pathlib import Path
import json

import sqlite3
import discord
from discord.ext import commands

from bot.config import *
from .cogs.prefix import set_default_prefix, delete_prefix_prefix


class Bot(commands.Bot):
    def __init__(self):
        self.client_id = None
        self._cogs = [p.stem for p in Path(".").glob(PATH_TO_COGS)]
        print(self._cogs)
        self._prefix = '>'

        super().__init__(command_prefix=self._prefix, case_insensitive=True, intents=discord.Intents.all())

    async def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            print(f"bot.cogs.{cog}")
            await self.load_extension(f"bot.cogs.{cog}")
            print(f" Loaded `{cog}` cog.")

        print("Setup complete.")

    def run(self):

        print("Running bot...")
        super().run(BOT_TOKEN, reconnect=True)

    async def setup_hook(self) -> None:
        print("Running setup_hook...")

        #con = sqlite3.connect(PATH_TO_LEVELS_DB)
        #con.close()

        self.remove_command("help")
        async for guild in self.fetch_guilds():
            self.tree.clear_commands(guild=discord.Object(id=guild.id))

        for cog in self._cogs:
            print(f"bot.cogs.{cog}")
            await self.load_extension(f"bot.cogs.{cog}")
            print(f" Loaded `{cog}` cog.")
        async for guild in self.fetch_guilds():
            # with open(PATH_TO_PREFIXES, 'r') as file:
            #     prefixes = json.load(file)
            # prefixes[str(guild.id)] = '>'
            # with open(PATH_TO_PREFIXES, 'w') as file:
            #     json.dump(prefixes, file, indent=4)
            await self.tree.sync(guild=discord.Object(id=guild.id))
        await self.tree.sync(guild=None)

        print(f'Sync for {self.user}')

    async def shutdown(self):
        print("Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f"Connected to Discord (latency: {self.latency * 1000:,.0f} ms).")

    async def on_resumed(self):
        print("Bot resumed.")

    async def on_disconnect(self):
        self.voice_clients[self.client_id].cleanup()
        print("Bot disconnected.")

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("Bot ready.")

    async def on_guild_join(self, guild):
        set_default_prefix(guild)

    async def on_guild_remove(self, guild):
        delete_prefix_prefix(guild)

    # async def on_raw_reaction_add(self, payload):
    #     if payload.user_id == self.client_id:
    #         return
    #     await self.invoke(payload, self.get_command("game_reaction"))


    async def prefix(self, bot, msg):
        # return commands.when_mentioned_or(">")(bot, msg)
        # with open(PATH_TO_PREFIXES, 'r') as file:
        #    prefixes = json.load(file)
        # return prefixes[str(msg.guild.id)]
        pass

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)
