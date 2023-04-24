import datetime
import disnake
from disnake.ext import commands
import EmbedPalette
import LogData
import debug_LogData

RULE_LABELS = [
    "[RULES]",
    "[ADMIN RULES]",
    "[QUESTIONNAIRE RULES]",
    "[QUESTIONNAIRE EXAMPLE]",
    "[PUNISHMENTS]",
    "[NAVIGATION]"
]


class RulePublish(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.guild = None
        self.bot = bot
        self.rules_maker_chan = []
        self.rules_chan = None
        self.rules_chan_hist = []
        self.rules_admin_chan = None
        self.rules_admin_chan_hist = []
        self.qrules_example = None
        self.qrules_example_hist = []
        self.qrules = None
        self.qrules_hist = []
        self.punishment = None
        self.punishment_hist = []
        self.navigation = None
        self.navigation_hist = []

    @staticmethod
    async def select_color(label):
        if label == RULE_LABELS[0]:
            return EmbedPalette.WARNING
        elif label == RULE_LABELS[1]:
            return EmbedPalette.WARNING
        elif label == RULE_LABELS[2]:
            return EmbedPalette.NOTES
        elif label == RULE_LABELS[3]:
            return EmbedPalette.EXAMPLE
        elif label == RULE_LABELS[4]:
            return EmbedPalette.IMPORTANT
        elif label == RULE_LABELS[5]:
            return EmbedPalette.EXAMPLE

    async def get_chan_rules(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_chan = self.bot.get_channel(LogData.RULE_CHANNEL)
        self.rules_chan_hist = await self.rules_chan.history().flatten()
        self.rules_chan_hist.reverse()
        self.rules_chan_hist = self.rules_chan_hist[1:]

    async def get_chan_admin_rules(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.rules_admin_chan = self.bot.get_channel(LogData.RULE_ADMIN_CHANNEL)
        self.rules_admin_chan_hist = await self.rules_admin_chan.history().flatten()
        self.rules_admin_chan_hist.reverse()

    async def get_chan_qexample(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.qrules_example = self.bot.get_channel(LogData.Q_EXAMPLE_CHANNEL)
        self.qrules_example_hist = await self.qrules_example.history().flatten()
        self.qrules_example_hist.reverse()

    async def get_chan_qrules(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.qrules = self.bot.get_channel(LogData.Q_RULE_CHANNEL)
        self.qrules_hist = await self.qrules.history().flatten()
        self.qrules_hist.reverse()

    async def get_chan_punishment(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.punishment = self.bot.get_channel(LogData.PUNISH_CHANNEL)
        self.punishment_hist = await self.punishment.history().flatten()
        self.punishment_hist.reverse()

    async def get_chan_navigation(self):
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.navigation = self.bot.get_channel(LogData.NAVIGATOR_CHANNEL)
        self.navigation_hist = await self.navigation.history().flatten()
        self.navigation_hist.reverse()

    async def get_maker_msgs(self, label):
        self.rules_maker_chan = [message for message in
                                 await self.bot.get_channel(LogData.RULE_MAKER_CHANNEL).history().flatten()
                                 if message.content.split("\n")[0] == label]
        self.rules_maker_chan.reverse()

    @staticmethod
    async def msg_publish_mode(msg_chan_count, msg_maker_count):
        if msg_chan_count == msg_maker_count:
            return 0
        elif msg_chan_count > msg_maker_count:
            return 1
        elif msg_chan_count < msg_maker_count:
            return 2

    async def send_embed(self, color: hex, channel, title, desc, attach_url):
        await channel.send(embed=disnake.Embed(title=title, description=desc, color=color).set_footer(
            text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url).set_image(
            url=attach_url
        ))

    async def edit_embed(self, color: hex, message, new_title, new_desc, new_attach):
        await message.edit(embed=disnake.Embed(title=new_title, description=new_desc, color=color
                                               ).set_footer(
            text=f"Утверждено от {datetime.datetime.now().date()}", icon_url=self.guild.icon.url).set_image(
            url=new_attach
        ))

    @staticmethod
    async def tandd_check(lable, maker_content, rules_content=None):
        if not maker_content == lable:
            if len(maker_content.split("\n")) > 2:
                new_title = maker_content.split("\n")[1]
                new_desc = maker_content[maker_content.find(maker_content.split("\n")[2]):]
            else:
                new_title = maker_content.split("\n")[1]
                new_desc = ""
        else:
            new_title = ""
            new_desc = ""
        if rules_content:
            past_title = "" if not rules_content.embeds[0].title else rules_content.embeds[0].title
            past_desc = "" if not rules_content.embeds[0].description else rules_content.embeds[0].description
            return new_title, new_desc, past_title, past_desc
        return new_title, new_desc

    async def mode_zero(self, lable, point_channel_hist_list: list[disnake.Message], length=None):
        color = await self.select_color(lable)
        if not length:
            length = len(point_channel_hist_list)
        for i in range(length):
            new_title, new_desc, past_title, past_desc = await self.tandd_check(lable,
                                                                                self.rules_maker_chan[i].content,
                                                                                point_channel_hist_list[i])
            past_content = past_title + past_desc
            new_content = new_title + new_desc
            new_attach = self.rules_maker_chan[i].attachments
            if new_attach:
                new_attach = new_attach[0].url
            else:
                new_attach = None
            past_attach = point_channel_hist_list[i].embeds[0].image.url
            if (past_content != new_content) or (past_attach != new_attach):
                await self.edit_embed(color, point_channel_hist_list[i], new_title, new_desc, new_attach)

    async def mode_one(self, lable, point_channel_hist_list: list[disnake.Message]):
        await self.mode_zero(lable, point_channel_hist_list, len(self.rules_maker_chan))
        for i in range(len(self.rules_maker_chan), len(point_channel_hist_list)):
            await point_channel_hist_list[i].delete()

    async def mode_two(self, lable, channel, point_channel_hist_list: list[disnake.Message]):
        color = await self.select_color(lable)
        await self.mode_zero(lable, point_channel_hist_list)
        attach = self.rules_maker_chan[len(point_channel_hist_list)].attachments
        for i in range(len(point_channel_hist_list), len(self.rules_maker_chan)):
            title, desc = await self.tandd_check(lable, self.rules_maker_chan[i].content)
            if attach:
                attach = attach[0].url
            else:
                attach = None
            await self.send_embed(color, channel, title, desc, attach)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="rulepublish",
        description="Публикация/обновление общих правил",
    )
    async def rulespublish(self, ctx):
        lable = "[RULES]"
        await self.get_chan_rules()
        await self.get_maker_msgs(lable)
        chan_len = len(self.rules_chan_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.rules_chan_hist)
        elif mode == 1:
            await self.mode_one(lable, self.rules_chan_hist)
        elif mode == 2:
            await self.mode_two(lable, self.rules_chan, self.rules_chan_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="adminpublish",
        description="Публикация/обновление правил для администраторов",
    )
    async def adminrulepublish(self, ctx):
        lable = "[ADMIN RULES]"
        await self.get_chan_admin_rules()
        await self.get_maker_msgs(lable)
        chan_len = len(self.rules_admin_chan_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.rules_admin_chan_hist)
        elif mode == 1:
            await self.mode_one(lable, self.rules_admin_chan_hist)
        elif mode == 2:
            await self.mode_two(lable, self.rules_admin_chan, self.rules_admin_chan_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="qrules",
        description="Публикация/обновление правил для оформления анкет",
    )
    async def qrules(self, ctx):
        lable = "[QUESTIONNAIRE RULES]"
        await self.get_chan_qrules()
        await self.get_maker_msgs(lable)
        chan_len = len(self.qrules_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.qrules_hist)
        elif mode == 1:
            await self.mode_one(lable, self.qrules_hist)
        elif mode == 2:
            await self.mode_two(lable, self.qrules, self.qrules_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="qexample",
        description="Публикация/обновление примера анкеты",
    )
    async def qexample(self, ctx):
        lable = "[QUESTIONNAIRE EXAMPLE]"
        await self.get_chan_qexample()
        await self.get_maker_msgs(lable)
        chan_len = len(self.qrules_example_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.qrules_example_hist)
        elif mode == 1:
            await self.mode_one(lable, self.qrules_example)
        elif mode == 2:
            await self.mode_two(lable, self.qrules_example, self.qrules_example_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="punishpublic",
        description="Публикация/обновление наказаний",
    )
    async def punishpublic(self, ctx):
        lable = "[PUNISHMENTS]"
        await self.get_chan_punishment()
        await self.get_maker_msgs(lable)
        chan_len = len(self.punishment_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.punishment_hist)
        elif mode == 1:
            await self.mode_one(lable, self.punishment_hist)
        elif mode == 2:
            await self.mode_two(lable, self.punishment, self.punishment_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="navpublic",
        description="Публикация/обновление навигации",
    )
    async def navpublic(self, ctx):
        lable = "[NAVIGATION]"
        await self.get_chan_navigation()
        await self.get_maker_msgs(lable)
        chan_len = len(self.navigation_hist)
        maker_len = len(self.rules_maker_chan)
        mode = await self.msg_publish_mode(chan_len, maker_len)
        if mode == 0:
            await self.mode_zero(lable, self.navigation_hist)
        elif mode == 1:
            await self.mode_one(lable, self.navigation_hist)
        elif mode == 2:
            await self.mode_two(lable, self.navigation, self.navigation_hist)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(
        name="annonce",
        description="Сделать объявление",
        options=[disnake.Option(
            name="num",
            description="Номер макета объявления который нужно отправить",
            required=True,
            choices=[
                disnake.OptionChoice(name="Первый макет", value=1),
                disnake.OptionChoice(name="Второй макет", value=2),
                disnake.OptionChoice(name="Третий макет", value=3),
                disnake.OptionChoice(name="Четвёртый макет", value=4),
                disnake.OptionChoice(name="Пятый макет", value=5),
            ],
            type=disnake.OptionType.integer
        )]
    )
    async def annonce(self, ctx, num):
        channel = self.bot.get_channel(LogData.ANNONCEMENT_CHANNEL)
        maker = self.bot.get_channel(LogData.ANNONCEMENT_MAKER_CHANNEL)
        maker_hist = await maker.history().flatten()
        for _ in maker_hist:
            msg_splited = _.content.split('\n')
            if msg_splited[0] == f"[ANNONCEMENT {num}]":
                attach = _.attachments
                embed = disnake.Embed(
                    title=msg_splited[3],
                    description=_.content[_.content.find(msg_splited[3]) + len(msg_splited[3]) + 1:],
                    color=int(msg_splited[2], 16)
                )
                mentions = ""
                if msg_splited[1] != "None":
                    mentions = msg_splited[1].replace(', ', '\n')
                await channel.send(f"{mentions}", embed=embed)


def setup(bot) -> None:
    bot.add_cog(RulePublish(bot))
