import logging

from app.bot.setup import bot
from app.constants import SECRET_TOKEN

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    bot.run(SECRET_TOKEN)
