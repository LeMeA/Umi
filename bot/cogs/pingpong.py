from discord.ext import commands


class PingPong(commands.Cog):
    def __init__(self):
        pass

    @commands.hybrid_command(name='ping', with_app_command=True, description='Return Pong.')
    async def ping(self, ctx: commands.Context):
        await ctx.send('Pong!')

async def setup(bot):
    await bot.add_cog(PingPong(bot))
