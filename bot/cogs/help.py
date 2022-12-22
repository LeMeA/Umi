import discord
from discord.ext import commands
from discord import app_commands
import typing as t

class MyHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", with_app_command=True, description='Bot help.')
    @app_commands.describe(
        plugin='Command or Cog name',
    )
    async def help(self, ctx, *, plugin: t.Optional[str] = None):
        if plugin is None:
            return await ctx.send(embed=self.send_help())

        cog = self.bot.get_cog(plugin)
        if cog is not None:
            return await ctx.send(embed=self.send_cog_help(cog))

        keys = plugin.split(' ')

        for key in keys:
            found = self.bot.all_commands.get(key)
            if found is not None:
                await ctx.send(embed=self.send_command_help(found))
            else:
                await ctx.send(embed=self.send_error_message(key))


    def send_help(self):
        embed = discord.Embed(
            title='Bot help (write >help <Cog/Command name>)',
            # url="",
            description="Available cogs:",
            color=discord.Color.red())
        # `mapping` is a dict of the bot's cogs, which map to their commands
        for name, cog in self.bot.cogs.items():
            if name == 'MyHelpCommand':
                continue
            embed.add_field(
                name=cog.qualified_name,  # get the cog name
                value=f"{len(cog.get_commands())} commands"  # get a count of the commands in the cog.
            )
        embed.set_author(name='Umi Bot',
                         icon_url='https://i.ibb.co/XFp2CGm/umi.png')
        return embed

    def send_cog_help(self, cog):
        """This is triggered when !help <cog> is invoked."""
        embed = discord.Embed(
            title=cog.qualified_name,
            # url="",
            description="Available bot commands",
            color=discord.Color.red())
        embed.set_author(name='Umi Bot',
                         icon_url='https://i.ibb.co/XFp2CGm/umi.png')
        for command in cog.get_commands():
            embed.add_field(name=f">{command.name}", value=f"{command.description}", inline=False)
        return embed

    def send_command_help(self, command):
        embed = discord.Embed(
            title=f'>{command.name}',
            # url="",
            description=command.description,
            color=discord.Color.red())
        embed.set_author(name='Umi Bot',
                         icon_url='https://i.ibb.co/XFp2CGm/umi.png')
        return embed


    def send_error_message(self, error):
        embed = discord.Embed(
            title=f'Error',
            # url="",
            description=f'Can\'t find references for {error}',
            color=discord.Color.red())
        embed.set_author(name='Umi Bot',
                         icon_url='https://i.ibb.co/XFp2CGm/umi.png')
        return embed

async def setup(bot):
    await bot.add_cog(MyHelpCommand(bot))
    #bot.help_command = MyHelpCommand()
