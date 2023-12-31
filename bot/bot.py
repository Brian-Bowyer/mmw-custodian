import discord

bot = discord.Bot()


@bot.command(description="Pings the bot")
async def ping(ctx) -> None:
    await ctx.respond("Pong!")
