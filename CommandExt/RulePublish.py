import disnake
from disnake.ext import commands

class RulePublish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.channel.id == 123456789:
    #         await message.add_reaction("✅")
    #         await message.add_reaction("❌")