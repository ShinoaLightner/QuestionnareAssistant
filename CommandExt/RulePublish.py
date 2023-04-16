import datetime
import disnake
from disnake.ext import commands

import EmbedPalette
import LogData

RULE_LABELS = [
    "[RULES]",
    "[ADMIN RULES]"
]


class RulePublish(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot
        self.rules_maker_chan = []
        self.rules_chan = None
        self.rules_admin_chan = None
        self.guild = None

    async def get_chan(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_maker_chan = await self.bot.get_channel(LogData.RULE_MAKER_CHANNEL).history().flatten()
        self.rules_maker_chan.reverse()
        self.rules_chan = self.bot.get_channel(LogData.RULE_CHANNEL)
        self.rules_admin_chan = self.bot.get_channel(LogData.RULE_ADMIN_CHANNEL)

    @commands.slash_command(
        name="rulepublish",
    )
    async def rulepublish(self, ctx):
        await self.get_chan()
        for message in self.rules_maker_chan:
            msg = message.content.split("\n")
            if msg[0] == RULE_LABELS[0]:
                await self.rules_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                       message.content.find(msg[2]):],
                                                           color=EmbedPalette.WARNING).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}",icon_url=self.guild.icon.url))
            elif msg[0] == RULE_LABELS[1]:
                await self.rules_admin_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                        message.content.find(msg[2]):],
                                                           color=EmbedPalette.WARNING).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url))
            else:
                pass


def setup(bot) -> None:
    bot.add_cog(RulePublish(bot))
