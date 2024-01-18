import logging

import discord

from app.controllers import initiative
from app.errors import AlreadyExistsError, NotFoundError

log = logging.getLogger(__name__)


def add_init_commands(bot: discord.Bot):
    log.info("Adding initiative commands")
    init_commands = bot.create_group("init", "commands relating to initiative")

    @init_commands.command()
    async def start(ctx):
        try:
            tracker = await initiative.create_initiative(ctx.channel.id)
        except AlreadyExistsError:
            await ctx.respond("Initiative tracker already exists!")
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def end(ctx):
        await initiative.delete_initiative(ctx.channel.id)
        await ctx.respond("Initiative tracker ended!")

    @init_commands.command()
    async def add(ctx, player: str, init_value: int, tiebreaker: int = 0):
        try:
            tracker = await initiative.add_participant(ctx.channel.id, player, init_value)
        except AlreadyExistsError:
            await ctx.respond(
                f"{player} is alrerady in this initiative! (use `update` to change their init value))"
            )
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def remove(ctx, player: str):
        try:
            tracker = await initiative.remove_participant(ctx.channel.id, player)
        except NotFoundError:
            await ctx.respond(f"{player} does not exist in this initiative!")
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def update(ctx, player: str, init_value: int, tiebreaker: int = 0):
        try:
            tracker = await initiative.update_participant(
                ctx.channel.id, player, init_value
            )
        except NotFoundError:
            await ctx.respond(f"{player} does not exist in this initiative!")
        else:
            await ctx.respond(str(tracker))

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
