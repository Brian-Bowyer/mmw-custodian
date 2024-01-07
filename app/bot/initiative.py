from discord import SlashCommandGroup
from discord.ext.commands import Context

init_commands = SlashCommandGroup("init", "commands relating to initiative")


@init_commands.command()
async def start(ctx: Context):
    pass


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


def setup(bot):
    bot.add_application_command(init_commands)
