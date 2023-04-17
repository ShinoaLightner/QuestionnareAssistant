import datetime
import disnake
from disnake.ext import commands

import EmbedPalette
import LogData

RULE_LABELS = [
    "[RULES]",
    "[ADMIN RULES]",
    "[QUESTIONNAIRE RULES]",
    "[QUESTIONNAIRE EXAMPLE]"
]


class RulePublish(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot
        self.rules_maker_chan = []
        self.rules_chan = None
        self.rules_admin_chan = None
        self.guild = None
        self.qrules_chan = None
        self.qexample_chan = None

    async def get_chan_rules(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_maker_chan = await self.bot.get_channel(LogData.RULE_MAKER_CHANNEL).history().flatten()
        self.rules_maker_chan.reverse()
        self.rules_chan = self.bot.get_channel(LogData.RULE_CHANNEL)
        self.rules_admin_chan = self.bot.get_channel(LogData.RULE_ADMIN_CHANNEL)

    async def get_chan_qrules(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_maker_chan = await self.bot.get_channel(LogData.RULE_MAKER_CHANNEL).history().flatten()
        self.rules_maker_chan.reverse()
        self.qrules_chan = self.bot.get_channel(LogData.Q_RULE_CHANNEL)

    async def get_chan_qexample(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_maker_chan = await self.bot.get_channel(LogData.RULE_MAKER_CHANNEL).history().flatten()
        self.rules_maker_chan.reverse()
        self.qexample_chan = self.bot.get_channel(LogData.Q_EXAMPLE_CHANNEL)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="rulepublish",
        description="Публикация правил",
    )
    async def rulepublish(self, ctx):
        await self.get_chan_rules()
        for message in self.rules_maker_chan:
            msg = message.content.split("\n")
            if msg[0] == RULE_LABELS[0]:
                await self.rules_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                                         message.content.find(msg[2]):],
                                                               color=EmbedPalette.WARNING).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url))
            elif msg[0] == RULE_LABELS[1]:
                await self.rules_admin_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                                               message.content.find(
                                                                                                   msg[2]):],
                                                                     color=EmbedPalette.WARNING).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url))
            else:
                pass

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="qrules",
        description="Публикация правил оформления анкет",
    )
    async def qrules(self, ctx):
        await self.get_chan_qrules()
        for message in self.rules_maker_chan:
            msg = message.content.split("\n")
            if msg[0] == RULE_LABELS[2]:
                if message.attachments:
                    url = message.attachments[0].url
                else:
                    url = None
                await self.qrules_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                                          message.content.find(
                                                                                              msg[2]):],
                                                                color=EmbedPalette.NOTES).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url).set_image(
                    url=url))
            else:
                pass

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="qexample",
        description="Публикация правил оформления анкет",
    )
    async def qexample(self, ctx):
        await self.get_chan_qexample()
        for message in self.rules_maker_chan:
            msg = message.content.split("\n")
            if msg[0] == RULE_LABELS[3]:
                if message.attachments:
                    url = message.attachments[0].url
                else:
                    url = None
                await self.qexample_chan.send(embed=disnake.Embed(title=msg[1], description=message.content[
                                                                                            message.content.find(
                                                                                                msg[2]):],
                                                                  color=EmbedPalette.EXAMPLE).set_footer(
                    text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url).set_image(
                    url=url))
            else:
                pass


def setup(bot) -> None:
    bot.add_cog(RulePublish(bot))
