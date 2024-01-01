from discord import SlashCommandGroup

init_commands = SlashCommandGroup("init", "commands relating to initiative")


@init_commands.command()
async def start(ctx):
    pass


@init_commands.command()
async def end(ctx):
    pass


@init_commands.command()
async def add(ctx, player: str, num: int):
    pass


@init_commands.command()
async def remove(ctx, player: str):
    pass


@init_commands.command()
async def update(ctx, player: str, num: int):
    pass


def setup(bot):
    bot.add_application_command(init_commands)
