import logging

import discord

from app.bot.initiative import setup as setup_init
from app.constants import TESTING_SERVERS

log = logging.getLogger(__name__)
bot = discord.Bot()


@bot.command(guild_ids=TESTING_SERVERS, description="Pings the bot")
async def ping(ctx) -> None:
    await ctx.respond("Pong!")


@bot.event
async def on_ready():
    setup_init(bot)
    log.info("MMW custodian running!")
