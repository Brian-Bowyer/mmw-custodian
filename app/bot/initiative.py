import logging

import discord
from discord.ext.commands import Context

from app.controllers import initiative

log = logging.getLogger(__name__)


def add_init_commands(bot: discord.Bot):
    log.info("Adding initiative commands")
    init_commands = bot.create_group("init", "commands relating to initiative")

    @init_commands.command()
    async def start(ctx: Context):
        await initiative.create_initiative(ctx.channel)
        print("Initiative created!")

    @init_commands.command()
    async def end(ctx: Context):
        pass

    @init_commands.command()
    async def add(ctx: Context, player: str, init_value: int):
        pass

    @init_commands.command()
    async def remove(ctx: Context, player: str):
        pass

    @init_commands.command()
    async def update(ctx: Context, player: str, init_value: int):
        pass

    @init_commands.command()
    async def next(ctx: Context):
        pass

    @init_commands.command()
    async def back(ctx: Context):
        pass

    @init_commands.command()
    async def goto(ctx: Context, current_init: int):
        # TODO support setting by init or player?
        pass

    log.info("Initiative commands added!")
