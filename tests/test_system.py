# Tests system commands like ping
import discord.ext.test as testcord
import pytest
from discord.ext.commands import Bot, Context
from discord.message import Message


@pytest.fixture
def bot(event_loop) -> Bot:
    bot = Bot(loop=event_loop)
    testcord.configure(bot)
    return bot


class TestPingCommand:
    @pytest.mark.asyncio
    async def test_ping(self, bot: Bot):
        """Tests the ping command"""
        await testcord.invoke(bot, "ping")
