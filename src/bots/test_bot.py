from discord import Intents
from discord.ext import tasks
from discord.ext.commands import Bot

from config import SETTINGS
from src.bots.bot import BaseBot

__all__ = (
    "TestBot"
)


class TestBot(BaseBot):

    def __init__(self):
        init_cogs = ()
        tasks_func = ((self.print_hello_world, (False, None)),
                      (self.print_go_sleep, (True, "12 hour")), )
        super(TestBot, self).__init__(init_cogs)

    @tasks.loop(seconds=10)
    async def print_hello_world(self):
        print("hello world")

    @staticmethod
    async def print_go_sleep():
        print("go sleep")
