import discord
import asyncio

NOT_CONNECTED, ALREADY_PLAYING, CONNECTED = 0, 1, 2
DISCONNECTED = 1
NO_QUERY, BAD_QUAEY= 0, 1

def send_non_async(msg, loop):
    asyncio.run_coroutine_threadsafe(msg, loop)

async def embed_track(ctx, player):
    guild_id = ctx.message.guild.id
    embed = discord.Embed(
        title=player.track_title(),
        # url="",
        # description="Here are some ways to format text",track_artist_cover
        color=discord.Color.red())
    embed.set_author(name='Umi Bot',
                     icon_url='https://i.ibb.co/4STnGZs/umi.png')
    embed.set_thumbnail(url=player.track_cover())
    await ctx.send(embed=embed)


async def embed_connected(ctx, type: int):
    msgs = [
        "You are not connected to any channel.",
        "Already playing in another channel.",
        "Let start disco!"
    ]
    embed = discord.Embed(
        title=msgs[type],
        # url="",
        # description="Here are some ways to format text",track_artist_cover
        color=discord.Color.red())
    embed.set_author(name='Umi Bot',
                     icon_url='https://i.ibb.co/4STnGZs/umi.png')
    await ctx.send(embed=embed)


async def embed_disconnected(ctx, type: int):
    msgs = [
        "Bot not connected.",
        "Disconnected.",
    ]
    embed = discord.Embed(
        title=msgs[type],
        # url="",
        # description="Here are some ways to format text",track_artist_cover
        color=discord.Color.red())
    embed.set_author(name='Umi Bot',
                     icon_url='https://i.ibb.co/4STnGZs/umi.png')
    await ctx.send(embed=embed)


async def embed_query(ctx, type: int):
    msgs = [
        "No query track.",
        "Can't find track with this query."
    ]
    embed = discord.Embed(
        title=msgs[type],
        # url="",
        # description="Here are some ways to format text",track_artist_cover
        color=discord.Color.red())
    embed.set_author(name='Umi Bot',
                     icon_url='https://i.ibb.co/4STnGZs/umi.png')
    await ctx.send(embed=embed)


async def embed_commands(self, ctx):
    embed = discord.Embed(title='COMMANDS',
                        # url="",
                        description="Available bot commands",
                        color=discord.Color.red())
    embed.add_field(name=">commands", value="Show available bot commands.", inline=False)
    embed.add_field(name=">play", value="Find track for queue.", inline=False)
    embed.add_field(name=">join", value="Join voice channel.", inline=False)
    embed.add_field(name=">leave", value="Leave voice channel.", inline=False)
    embed.add_field(name=">stop", value="Stop current queue/playlist.", inline=False)
    embed.add_field(name=">playlist", value="Find playlist by url.", inline=False)
    embed.add_field(name=">skip", value="Skip track.", inline=False)
    embed.add_field(name=">resume", value="Resume paused track.", inline=False)
    embed.add_field(name=">pause", value="Pause playing track.", inline=False)
    embed.add_field(name=">shuffle", value="Shuffle tracks in playlist.", inline=False)
    await ctx.send(embed=embed)