import logging

import discord

from app.controllers import initiative
from app.errors import AlreadyExistsError, BacktrackError, NotFoundError

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
        try:
            await initiative.delete_initiative(ctx.channel.id)
        except NotFoundError:
            await ctx.respond("No initiative tracker found!")
        else:
            await ctx.respond("Initiative tracker ended!")

    @init_commands.command()
    async def show(ctx):
        try:
            tracker = await initiative.get_initiative(ctx.channel.id)
        except NotFoundError:
            await ctx.respond("No initiative tracker found!")
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def add(ctx, player: str, init_value: int, tiebreaker: int = 0):
        try:
            tracker = await initiative.add_participant(
                ctx.channel.id, player, init_value
            )
        except NotFoundError:
            await ctx.respond("No initiative tracker found!")
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
        try:
            tracker = await initiative.next_participant(ctx.channel.id)
        except NotFoundError:
            await ctx.respond("No tracker found!")
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def back(ctx):
        try:
            tracker = await initiative.previous_participant(ctx.channel.id)
        except NotFoundError:
            await ctx.respond("No tracker found!")
        except BacktrackError:
            await ctx.respond("Cannot go back any further!")
        else:
            await ctx.respond(str(tracker))

    @init_commands.command()
    async def goto(ctx, target_name: str) -> None:
        try:
            tracker = await initiative.goto_participant(ctx.channel.id, target_name)
        except NotFoundError:
            await ctx.respond(f"{target_name} does not exist in this initiative!")
        else:
            await ctx.respond(str(tracker))

    log.info("Initiative commands added!")
