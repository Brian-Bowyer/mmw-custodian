import logging

import discord

from app.controllers import initiative

log = logging.getLogger(__name__)


def add_init_commands(bot: discord.Bot):
    log.info("Adding initiative commands")
    init_commands = bot.create_group("init", "commands relating to initiative")

    @init_commands.command()
    async def start(ctx):
        log.info("Starting initiative tracker...")
        await initiative.create_initiative(ctx.channel.id)
        log.info("Initiative tracker started!")
        await ctx.respond("Initiative tracker started!")

    @init_commands.command()
    async def end(ctx):
        pass

    @init_commands.command()
    async def add(ctx, player: str, init_value: int):
        pass

    @init_commands.command()
    async def remove(ctx, player: str):
        pass

    @init_commands.command()
    async def update(ctx, player: str, init_value: int):
        pass

    @init_commands.command()
    async def next(ctx):
        pass

    @init_commands.command()
    async def back(ctx):
        pass

    @init_commands.command()
    async def goto(ctx, current_init: int):
        # TODO support setting by init or player?
        pass

    log.info("Initiative commands added!")
