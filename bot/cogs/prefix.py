import json
from discord.ext import commands
from discord import app_commands
from ..config import PATH_TO_PREFIXES


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="change_prefix", with_app_command=True, description='Change prefix for bot.')
    @app_commands.describe(
        prefix='New prefix',
    )
    async def change_prefix(self, ctx, *, prefix: str):
        valid_prefix = ['!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '+', '=', '~', '>']
        if len(prefix) != 1 or prefix not in valid_prefix:
            return await ctx.send(f"Prefix {prefix} isn\'t valid. "
                                  f"(You can use: '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '+', '=', '~', '>')")
        self.set_new_prefix(ctx.guild, prefix)
        return await ctx.send(f"Prefix changed to: {prefix}")

    def set_new_prefix(self, guild, prefix):
        with open(PATH_TO_PREFIXES, 'r') as file:
            prefixes = json.load(file)
        prefixes[str(guild.id)] = prefix
        with open(PATH_TO_PREFIXES, 'w') as file:
            json.dump(prefixes, file, indent=4)


def set_default_prefix(guild):
    with open(PATH_TO_PREFIXES, 'r') as file:
        prefixes = json.load(file)
    prefixes[str(guild.id)] = '>'
    with open(PATH_TO_PREFIXES, 'w') as file:
        json.dump(prefixes, file, indent=4)


def delete_prefix_prefix(guild):
    with open(PATH_TO_PREFIXES, 'r') as file:
        prefixes = json.load(file)
    prefixes.pop(str(guild.id))
    with open(PATH_TO_PREFIXES, 'w') as file:
        json.dump(prefixes, file, indent=4)


async def setup(bot):
    await bot.add_cog(Prefix(bot))
