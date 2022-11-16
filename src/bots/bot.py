from asyncpg import Pool, create_pool
from discord import Intents, Object
from discord.ext.commands import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import SETTINGS


class BaseBot(Bot):

    def __init__(self, init_cogs: tuple[str, ...], tasks: tuple):
        """
        :param init_cogs: Обязательный аргумент для инцализации шестеренок.
        """
        super(BaseBot, self).__init__(command_prefix=SETTINGS["tokens"][self.__class__.__name__],
                                      intents=Intents.all())

        self.pool = None
        self.synced = False
        self.connected = False
        self.task = False
        self.init_cogs = init_cogs
        self.tasks = tasks

    async def setup_hook(self) -> None:
        for ext in self.init_cogs:
            await self.load_extension(ext)

    async def _synced(self):
        if not self.synced:
            self.synced = True

            await self.tree.sync(guild=Object(id=SETTINGS["server"]["id"]))
            print("[+] Команды были успешно обновлены.")

    async def _connect(self):
        if not self.connected:
            dns = SETTINGS["database"]["dsn"]

            if dns is not None:
                self.connected = True

                self.pool: Pool = await create_pool(dsn=dns, loop=self.loop)
                print("[+] Бот подключился к базе данных")
            else:
                print("[-] Бот не смог подключиться, так как не была указана в настройках")

    async def _task(self):
        self.task = True

        scheduler = AsyncIOScheduler()

        for task in self.tasks:
            if not task[1][0]:
                await task[0].start()
            else:
                scheduler.add_job(task[0], CronTrigger(minute=10))  # Каждые 10 минут
            scheduler.start()
        # Для задач просто с таймером
        # Используется Декоратор от discord.py
        #
        # Пример функции:
        # @tasks.loop()
        # async def test():
        #   ...
        #
        # Чтобы активировать: self.test.start()
        #
        #
        # Для точно запланированных задач
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(func, CronTrigger(minute=10)) # Каждые 10 минут
        # scheduler.start()

    async def on_ready(self):
        await self.wait_until_ready()

        await self._synced()

        await self._connect()

        await self._task()
