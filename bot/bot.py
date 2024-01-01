import discord
from constants import SECRET_TOKEN, TESTING_SERVERS
from initiative import setup as setup_init

bot = discord.Bot()


@bot.command(guild_ids=TESTING_SERVERS, description="Pings the bot")
async def ping(ctx) -> None:
    await ctx.respond("Pong!")


@bot.event
async def on_ready():
    setup_init(bot)
    print("MMW custodian running!")


if __name__ == "__main__":
    bot.run(SECRET_TOKEN)
