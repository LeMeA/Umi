import discord
import asyncio
import os
from discord.ext import commands
from discord import app_commands
import yandex_music
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from ..config import *
from .player.player import Player


class PlayQuery(commands.FlagConverter):
    query: str = commands.flag(description='Track name')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = {"SPOTIFY": Spotify(
            client_credentials_manager=SpotifyClientCredentials(client_id=CID, client_secret=SECRET)),
            "YANDEX": yandex_music.Client(YANDEX_TOKEN).init()
        }
        self.players = {}

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog Music is ready!')

    # Commands
    @commands.hybrid_command(name="join", with_app_command=True, description='Connect bot to user voice channel.')
    async def join(self, ctx):
        await ctx.defer(ephemeral=True)
        if ctx.message.author.voice is None:
            await ctx.send("You are not connected to any channel.")
            return False
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice_client is not None and voice_client.is_connected() is False and voice_client.is_playing() is True:
            voice_client.cleanup()
            voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None and voice_client.is_playing() is False:
            self.players[ctx.message.guild.id] = Player(ctx.message.guild.id)
            return await ctx.voice_client.move_to(ctx.message.author.voice.channel)
        elif voice_client is not None and voice_client.is_playing() is True \
                and voice_client.channel != ctx.message.author.voice.channel:
            return await ctx.send("Already playing in another channel.")

        self.create_folder(ctx.message.guild.id)
        self.players[ctx.message.guild.id] = Player(ctx.message.guild.id)
        channel = ctx.message.author.voice.channel
        await channel.connect(self_deaf=True)
        return await ctx.send("Connected. Let's start Disco.")

    @commands.hybrid_command(name="leave", with_app_command=True, description='Disconnect bot to user voice channel.')
    async def leave(self, ctx):
        await ctx.defer(ephemeral=True)
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            await voice_client.disconnect()
            voice_client.cleanup()
            return await ctx.send("Disconnected.")
        else:
            return await ctx.send("Bot not connected.")

    @commands.hybrid_command(name="play", with_app_command=True, description='Add track to queue and start Disco.')
    @app_commands.describe(
        query='Track name',
    )
    async def play(self, ctx, *, query: str):
        await ctx.defer(ephemeral=True)
        if len(query) == 0:
            return await ctx.send("No query track.")

        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None or voice_client.is_connected() is False:
            con = await self.join(ctx)
            if con is False:
                return
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if self.players[ctx.message.guild.id].paused:
            return await ctx.send("You have paused disco (Use >resume or >stop command).")

        if voice_client.is_playing() and self.players[ctx.message.guild.id].mode == 'PLAYLIST':
            return await ctx.send("Disco already started, stop it before new one.")


        if self.players[ctx.message.guild.id].add_to_queue(query) is False:
            return await ctx.send("Can't find track with this query.")
        if not voice_client.is_playing():
            self.after(ctx, ret=True)
            await self.embed_track(ctx)

    @commands.hybrid_command(name="playlist", with_app_command=True, description='Starts Disco with queried playlist.')
    @app_commands.describe(
        link='Playlist\'s link',
    )
    async def playlist(self, ctx, *, link: str):
        await ctx.defer(ephemeral=True)
        if len(link) == 0:
            return await ctx.send("No url.")

        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None or voice_client.is_connected() is False:
            con = await self.join(ctx)
            if con is False:
                return
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if self.players[ctx.message.guild.id].paused:
            return await ctx.send("You have paused disco (Use >resume or >stop command).")

        if voice_client.is_playing():
            return await ctx.send("Disco already started, stop it before new one.")

        if self.players[ctx.message.guild.id].set_playlist(link, self.client) is False:
            return await ctx.send("Playlist url is invalid.")
        self.after(ctx, ret=True)
        await self.embed_track(ctx)

    @commands.hybrid_command(name="stop", with_app_command=True, description='Stop any Disco.')
    async def stop(self, ctx):
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            self.players[ctx.message.guild.id] = Player(ctx.message.guild.id)
            if voice_client.is_playing():
                ctx.message.guild.voice_client.stop()
                return await ctx.send("Disco stopped.")
            else:
                return await ctx.send("Bot is not playing anything at the moment.")
        else:
            return await ctx.send("Bot not connected.")

    @commands.hybrid_command(name="skip", with_app_command=True, description='Skip track.')
    async def skip(self, ctx):
        await ctx.defer(ephemeral=True)
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice_client is None:
            return await ctx.send("Bot is not playing anything at the moment.")
        if voice_client.is_playing():
            ctx.message.guild.voice_client.stop()

    @commands.hybrid_command(name="pause", with_app_command=True, description='Pause Disco.')
    async def pause(self, ctx):
        await ctx.defer(ephemeral=True)
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None or not voice_client.is_connected():
            return await ctx.send("Bot not connected.")
        if voice_client.is_playing():
            voice_client.pause()
            self.players[ctx.message.guild.id].paused = True
            return await ctx.send("Paused.")
        else:
            await ctx.send("Bot is not playing anything at the moment.")

    @commands.hybrid_command(name="resume", with_app_command=True, description='Resume Disco.')
    async def resume(self, ctx):
        await ctx.defer(ephemeral=True)
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None or not voice_client.is_connected():
            return await ctx.send("Bot not connected.")
        if not self.players[ctx.message.guild.id].empty():
            self.players[ctx.message.guild.id].paused = False
            voice_client.resume()
            return await ctx.send("Resumed.")
        else:
            await ctx.send("Bot was not playing anything before this. Use **play** command")

    @commands.hybrid_command(name="shuffle", with_app_command=True, description='Shuffle playlist\'s tracks.')
    async def shuffle(self, ctx):
        await ctx.defer(ephemeral=True)
        if self.players[ctx.message.guild.id].turn_shuffle():
            if self.players[ctx.message.guild.id].f_shuffle:
                await ctx.send("Shuffle is on.")
            else:
                await ctx.send("Shuffle is off.")
        else:
            await ctx.send("Unable to shuffle queue.")

    # @commands.hybrid_command(name="commands", with_app_command=True, description='Show available bot commands.')
    # async def commands(self, ctx):
    #     await self.embed_commands(ctx)

    # Functions
    def after(self, ctx, ret=False):
        print('[FUNC]: after')
        guild_id = ctx.message.guild.id
        voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not self.players[guild_id].empty():
            print('[FUNC] after shuold play')
            voice_client: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            print('Before download')
            self.players[guild_id].download_next()
            print('before source')
            source = discord.FFmpegPCMAudio(PATH_TO_SERVERS + str(guild_id) + "/track.mp3")
            print('Source created')
            voice_client.play(source, after=lambda e: self.after(ctx))
            if ret is False:
                self.send_non_async(self.embed_track(ctx))
        else:
            pass

    def send_non_async(self, msg):
        asyncio.run_coroutine_threadsafe(msg, self.bot.loop)

    def create_folder(self, guild_id):
        if not os.path.exists(PATH_TO_SERVERS + str(guild_id)):
            os.mkdir(PATH_TO_SERVERS + str(guild_id))
            print(f"Folder for {guild_id} created.")

    async def embed_track(self, ctx):
        guild_id = ctx.message.guild.id
        embed = discord.Embed(
            title=self.players[guild_id].track_title(),
            # url="",
            # description="Here are some ways to format text",track_artist_cover
            color=discord.Color.red())
        embed.set_author(name='Umi Bot',
                         icon_url='https://i.ibb.co/XFp2CGm/umi.png')
        embed.set_thumbnail(url=self.players[guild_id].track_cover())
        await ctx.send(embed=embed)

    async def embed_commands(self, ctx):
        embed = discord.Embed(
            title='COMMANDS',
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


async def setup(bot):
    await bot.add_cog(Music(bot))
