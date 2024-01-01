import discord
from constants import SECRET_TOKEN, TESTING_SERVERS

bot = discord.Bot()


@bot.event
async def on_ready():
    print("MMW custodian running!")


@bot.command(guild_ids=TESTING_SERVERS, description="Pings the bot")
async def ping(ctx) -> None:
    await ctx.respond("Pong!")


if __name__ == "__main__":
    bot.run(SECRET_TOKEN)
