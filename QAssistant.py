import asyncio
import datetime
import platform
import disnake
from disnake.ext import commands, tasks
from colorama import Fore
import LogData
from DB_Ext.QManipulate import QManipulate

BOT_VERSION = "v1.0"


class QAssistant(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="\'\'", intents=disnake.Intents.all(), status=disnake.Status.online)
        self.sqlconnect = None
        self.qmanipulate = None
        self.cogs_list = ["CommandExt.PublishModule"]
        self.q_task = None
        self.setup_hook()
        print(f"{Fore.GREEN}Cogs Loaded!")

    def setup_hook(self):
        for cog in self.cogs_list:
            self.load_extension(cog)
            print(f"{Fore.GREEN}Loaded {Fore.YELLOW}{cog}")

    @tasks.loop(seconds=45)
    async def counter_status(self):
        try:
            await self.change_presence(activity=disnake.Game(name=f"qAssistant {BOT_VERSION}"))
            await asyncio.sleep(15)
            await self.change_presence(activity=disnake.Game(name=f"Кол-во анкет: {self.qmanipulate.qcount}"))
        except ConnectionResetError:
            print("Connection Reset Error: Restart a loop, check a bot!")
            await asyncio.sleep(5)

    async def on_ready(self):
        print(f"{Fore.GREEN}Logged in as {Fore.YELLOW}{self.user.name}#{self.user.discriminator}")
        print(f"{Fore.GREEN}ID: {Fore.YELLOW}{self.user.id}")
        print(f"{Fore.GREEN}Bot Version: {Fore.YELLOW}{BOT_VERSION}")
        print(f"{Fore.GREEN}Disnake Version: {Fore.YELLOW}{disnake.__version__}")
        print(f"{Fore.GREEN}Python Version: {Fore.YELLOW}{platform.python_version()}")
        print(f"{Fore.GREEN}Platform: {Fore.YELLOW}{platform.system()} {platform.release()}")
        print(f"{Fore.GREEN}Logged in at: {Fore.YELLOW}{datetime.datetime.now()}")
        print(f"{Fore.GREEN}Connecting to {Fore.YELLOW}SQLDB")
        self.qmanipulate = QManipulate(self)
        print(f"{Fore.GREEN}Connected to {Fore.YELLOW}QManipulate")
        print(f"{Fore.GREEN} Getting Channel for {Fore.YELLOW}QManipulate")
        await self.qmanipulate.get_chan()
        if not self.q_task:
            self.q_task = self.loop.create_task(self.qmanipulate.q_task())
        print(f"{Fore.GREEN}QTask Started!")
        print(f"{Fore.GREEN}Bot is ready! {Fore.YELLOW}{datetime.datetime.now()}")
        if not self.counter_status.is_running():
            self.counter_status.start()


if __name__ == "__main__":
    bot = QAssistant()
    bot.run(LogData.TOKEN)
