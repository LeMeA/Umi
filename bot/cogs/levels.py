import asyncio
from discord.utils import get
from discord.ext import commands
from discord import app_commands
import sqlite3
from ..config import *

sql_create_levels_table = f""" CREATE TABLE IF NOT EXISTS levels (
                                        guild_id integer PRIMARY KEY,
                                        user_id,
                                        user_name text,
                                        level integer,
                                        experience integer,
                                        new_lvl_exp integer,
                                    ); """


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mul = 1.3
        self.exp_speed = 10
        self.channel = None
        print('Levels')
        asyncio.run_coroutine_threadsafe(self.sync(), self.bot.loop)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        con = sqlite3.connect(PATH_TO_LEVELS_DB)
        cur = con.cursor()
        cur.execute(self.get_query("INSERT", member.guild.id), (member.id, member.name, 1, 0, 100))
        con.commit()
        con.close()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        con = sqlite3.connect(PATH_TO_LEVELS_DB)
        cur = con.cursor()
        self.create_table(cur, guild.id)
        async for member in guild.fetch_members(limit=None):
            cur.execute(self.get_query("SELECT_USER", guild.id), (member.id,))
            data = cur.fetchone()
            if data is None:
                cur.execute(self.get_query("INSERT", guild.id), (member.id, member.name, 1, 0, 100))
        con.commit()
        con.close()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.client_id or msg.content.startswith(">"):
            return
        else:
            con = sqlite3.connect(PATH_TO_LEVELS_DB)
            cur = con.cursor()
            self.create_table(cur, msg.guild.id)
            cur.execute(self.get_query("SELECT_USER", msg.guild.id), (msg.author.id,))
            data = cur.fetchone()
            if data is None:
                cur.execute(self.get_query("INSERT", msg.guild.id), (msg.author.id, msg.author.name, 1, 0, 100))
            else:
                await self.get_exp(msg.guild.id, msg.author.id, cur)

            con.commit()
            con.close()
            # cur.execute('UPDATE users SET ')

    @commands.hybrid_command(name="rank", with_app_command=False, description='Show user rank.')
    async def rank(self, ctx):
        con = sqlite3.connect(PATH_TO_LEVELS_DB)
        cur = con.cursor()
        cur.execute(self.get_query("GET_EXP", ctx.guild.id), (ctx.author.id,))
        data = cur.fetchone()
        await ctx.send(f"{ctx.author.name} level: {data[2]}. Experience: {data[0]}. Need: {data[1]}")
        con.close()

    @commands.hybrid_command(name="set_lvl_channel", with_app_command=False, description='Set default levels channel.')
    async def set_lvl_channel(self, ctx):
        self.channel = ctx
        await ctx.send(f"{ctx.message.channel.name} set for levels notifications.")

    # @commands.hybrid_command(name="sync_levels", with_app_command=False, description='sync_levels.')
    # async def sync_levels(self, ctx):
    #     if ctx.author.id != 242274813039738880:
    #         return
    #     await self.sync()

    async def sync(self):
        con = sqlite3.connect(PATH_TO_LEVELS_DB)
        cur = con.cursor()
        print('Sync')
        async for guild in self.bot.fetch_guilds():
            self.create_table(cur, guild.id)
            async for member in guild.fetch_members(limit=None):
                cur.execute(self.get_query("SELECT_USER", guild.id), (member.id,))
                data = cur.fetchone()
                if data is None:
                    cur.execute(self.get_query("INSERT", guild.id), (member.id, member.name, 1, 0, 100))
        print('Created')
        con.commit()
        con.close()

    async def get_exp(self, guild_id, user_id, cur):
        cur.execute(self.get_query("GET_EXP", guild_id), (user_id,))
        exp, new_lvl_exp, level = cur.fetchone()
        exp += self.exp_speed
        if exp >= new_lvl_exp:
            exp -= new_lvl_exp
            new_lvl_exp *= self.mul
            level += 1
            if self.channel is not None:
                user = get(self.bot.get_all_members(), id=user_id)
                await self.channel.send(f"{user.name} reached {level} level")
        cur.execute(self.get_query("UPDATE_LVL", guild_id), (level, exp, new_lvl_exp, user_id))

    def get_query(self, _type, guild_id):
        if _type == "SELECT_USER":
            return f"SELECT * FROM {self.table_name(guild_id)} WHERE user_id = ?"
        if _type == "INSERT":
            return f"INSERT INTO {self.table_name(guild_id)} VALUES(?, ?, ?, ?, ?);"
        if _type == "UPDATE_LVL":
            return f"UPDATE {self.table_name(guild_id)} SET level=?," \
                   f" experience=?, new_lvl_exp=? WHERE user_id=?"
        if _type == "GET_EXP":
            return f"SELECT experience, new_lvl_exp, level FROM {self.table_name(guild_id)} WHERE user_id = ?"

    def create_table(self, cur, guild_id):
        create_table_query = "CREATE TABLE IF NOT EXISTS {} ( user_id, " \
                       "user_name text, level integer, experience integer, " \
                             "new_lvl_exp integer);".format(self.table_name(guild_id))
        cur.execute(create_table_query)

    def table_name(self, guild_id):
        return "server_" + str(guild_id)


async def setup(bot):
    await bot.add_cog(Levels(bot))





