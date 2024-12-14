import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='>', case_insensitive=True, intents=discord.Intents.all())

    async def setup_hook(self):
        with open('cogs/enabled_cogs.txt', 'r') as enabled_cogs:
            for cog_name in enabled_cogs.readlines():
                await self.load_extension(f'bot.cogs.{cog_name}')
