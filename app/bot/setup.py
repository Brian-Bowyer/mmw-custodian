import logging

import discord

from app.bot.initiative import add_init_commands
from app.constants import TESTING_SERVERS
from app.models import database

log = logging.getLogger(__name__)
bot = discord.Bot()


@bot.command(guild_ids=TESTING_SERVERS, description="Pings the bot")
async def ping(ctx) -> None:
    await ctx.respond("Pong!")


@bot.event
async def on_ready():
    add_init_commands(bot)
    log.info("MMW custodian running!")


@bot.event
async def on_connect():
    await database.connect()
    log.info("Connected to database!")


@bot.event
async def on_disconnect():
    await database.disconnect()
    log.info("Disconnected from database!")
    log.info("MMW custodian shutting down!")
