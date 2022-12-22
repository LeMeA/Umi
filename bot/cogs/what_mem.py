import discord
from discord.ext import commands
from random import randint
from ..config import PATH_TO_MEM


class Card:
    def __init__(self, msg, url):
        self.msg = msg
        self.url = url
        self.reactions = 0
        self.user = None


class Player:
    def __init__(self, user):
        self.user = user
        self.cards = {}
        self.ready = False
        self.choose_winner = False

    def add_card(self, msg, url):
        self.cards[msg.id] = Card(msg, url)

    async def react_card(self, msg_id):
        if msg_id in self.cards.keys():
            self.ready = True
            await self.cards[msg_id].msg.delete()
            card = self.cards.pop(msg_id)
            return card
        return None


class WhatMem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.players = []
        self.ready = 0
        self.table_cards = {}
        self.f_started = False
        self.f_choose_card = False
        self.f_choose_winner = False
        self.cards_urls = []
        self.phrases = []

    @commands.hybrid_command(name="what_mem", with_app_command=False, description='Launch What mem game (beta 0.1.0).')
    async def what_mem(self, ctx):
        self.f_started = True
        self.channel = ctx
        self.load_cards_pool()
        return await ctx.send('What mem started (write <accept> to join).')

    @commands.hybrid_command(name="accept", with_app_command=False, description='Join to game.')
    async def accept(self, ctx):
        if self.f_started is False:
            return await ctx.send("Game not launched.")

        if self.f_choose_card is True or self.f_choose_winner is True:
            return await ctx.send("Wait for round's end.")

        for player in self.players:
            if player.user == ctx.message.author:
                return await ctx.send("You have already joined the game.")
        self.players.append((Player(ctx.message.author)))
        return await ctx.send(f"Welcome to the game {ctx.message.author.name}.")

    @commands.hybrid_command(name="out", with_app_command=False, description='Leave the game.')
    async def out(self, ctx):
        if self.f_started is False:
            return await ctx.send("Game not launched.")

        if self.f_choose_card is True or self.f_choose_winner is True:
            return await ctx.send("Wait for round's end.")

        for player in self.players:
            if player.user == ctx.message.author:
                await ctx.send(f"See you next time {ctx.message.author.name}.")
                return self.players.remove(player)
        return await ctx.send("You aren't in game.")

    @commands.hybrid_command(name="start", with_app_command=False, description='Start game.')
    async def start(self, ctx):
        if self.f_started is False:
            return await ctx.send("Game not launched.")

        self.f_choose_card = True
        for player in self.players:
            await self.send_cards_to_player(player)
        if len(self.phrases) == 0:
            await ctx.send('Phrases ends, game will be restarted.')
            await self.reset_game()
        idx = randint(0, len(self.phrases))
        url = self.phrases.pop(idx)
        await ctx.send(url)

    @commands.hybrid_command(name="end", with_app_command=False, description='End game.')
    async def end(self, ctx):
        if self.f_started is False:
            return await ctx.send("Game not launched.")
        await self.reset_game()
        self.f_started = False
        return await ctx.send("See you next time <3.")

    async def send_cards_to_player(self, player):
        for _ in range(4 - len(player.cards)):
            if len(self.cards_urls) == 0:
                self.channel.send("Cards for players ends. (Restarting game...).")
                await self.reset_game()
                return
            card_idx = randint(0, len(self.cards_urls) - 1)
            msg = await player.user.send(self.cards_urls[card_idx])
            player.add_card(msg, self.cards_urls[card_idx])
            await msg.add_reaction('✅')
            self.cards_urls.pop(card_idx)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.f_started is False:
            return
        if payload.user_id == self.bot.user.id:
            return

        if self.f_choose_card is True:
            await self.check_dm_reaction(payload)
        elif self.f_choose_winner is True:
            await self.check_table_reaction(payload)

    async def send_table(self):
        self.f_choose_winner, self.f_choose_card = True, False
        temp = self.table_cards.copy()
        self.table_cards.clear()
        for key in temp.keys():
            msg = await self.channel.send(temp[key].url)
            self.table_cards[msg.id] = Card(msg, temp[key].url)
            self.table_cards[msg.id].user = temp[key].user
            await msg.add_reaction('✅')

    def load_cards_pool(self):
        with open(PATH_TO_MEM + 'memes.txt', 'r') as memes_file:
            for line in memes_file:
                self.cards_urls.append(line)

        with open(PATH_TO_MEM + 'tasks.txt', 'r') as memes_file:
            for line in memes_file:
                self.phrases.append(line)

    async def check_dm_reaction(self, payload):
        user = self.bot.get_user(payload.user_id)
        card = None
        for player in self.players:
            if player.user == user and player.ready is not True:
                card = await player.react_card(payload.message_id)
                if card is not None:
                    self.ready += 1
                    self.table_cards[payload.message_id] = card
                    self.table_cards[payload.message_id].user = user
                else:
                    return
        if len(self.players) == self.ready:
            self.ready = 0
            await self.send_table()

    async def check_table_reaction(self, payload):
        user = self.bot.get_user(payload.user_id)
        card = None
        for player in self.players:
            if player.user == user and player.choose_winner is not True:
                if payload.message_id in self.table_cards.keys():
                    self.table_cards[payload.message_id].reactions += 1
                    player.choose_winner = True
                    self.ready += 1

        if len(self.table_cards) == self.ready:
            self.ready = 0
            await self.choose_winner()

    async def choose_winner(self):
        winners = [Card(None, None)]
        res = 'Winner(-s):'
        for card in self.table_cards.values():
            if winners[0].reactions < card.reactions:
                winners.clear()
                winners.append(card)
            elif winners[0].reactions == card.reactions:
                winners.append(card)
        for winner in winners:
            res += ' ' + winner.user.name
        self.f_choose_winner = False
        await self.channel.send(res + '.')
        self.next_game()

    def next_game(self):
        for player in self.players:
            player.ready, player.choose_winner = False, False
        self.f_choose_card, self.f_choose_winner = False, False
        self.table_cards.clear()

    async def reset_game(self):
        for player in self.players:
            for card in player.cards.values():
                await card.msg.delete()
        self.load_cards_pool()
        self.players = []
        self.ready = 0
        self.table_cards = {}
        self.f_started = True
        self.f_choose_card = False
        self.f_choose_winner = False
        self.cards_urls = []
        self.phrases = []


async def setup(bot):
    await bot.add_cog(WhatMem(bot))
