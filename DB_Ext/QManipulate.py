import io
import disnake
import LogData
import SQLDB
import datetime
import re
import asyncio
from disnake.ext import commands
import EmbedPalette

SAVE_DB_TIME = 300


class QManipulate:
    def __init__(self, bot: commands.Bot, sqlconnect: SQLDB.SQLDB):
        self.bot = bot
        self.sqlconnect = sqlconnect
        self.rp_hist = []
        self.char_hist = []
        self.char_chan = None
        self.rp_chan = None
        self.check_chan = None
        self.logs_chan = None
        self.logs_arch_chan = None
        self.archive_chan = None
        self.guild = None

    async def get_chan(self):
        self.check_chan = self.bot.get_channel(LogData.Q_CHECK_CHANNEL)
        self.logs_chan = self.bot.get_channel(LogData.Q_LOG_CHANELL)
        self.guild = self.bot.get_guild(LogData.Q_GUILD_ID)
        self.char_chan = self.bot.get_channel(LogData.Q_CHAR_CHANELL)
        self.rp_chan = self.bot.get_channel(LogData.Q_RP_CHANELL)
        self.logs_arch_chan = self.bot.get_channel(LogData.Q_ARCHIVE_LOG_CHANELL)
        self.archive_chan = self.bot.get_channel(LogData.Q_ARCHIVE_CHANELL)

    @staticmethod
    async def mention_slicer(msg_content: str) -> int:
        if msg_content.find('<@!') == -1:
            first_index = msg_content.find('<@') + 2
        else:
            first_index = msg_content.find('<@!') + 3
        message_txt = msg_content[first_index:]
        end_index = message_txt.find('>')
        mention = int(message_txt[:end_index])
        return mention

    async def prefs_slicer(self, msg: disnake.Message) -> str or bool:
        msg_content = msg.content.split('\n')
        msg_content = [_.replace('*', '') for _ in msg_content]
        regex = re.compile("(^[0-9]\\.)|"
                           "(^[0-9]\\))|"
                           "(^[\U0001F000-\U0001FFFF]|"
                           "(^[\\u2600-\\u2FFF])|"
                           "(.*\\u200D.*)|"
                           "(.*\\uFE0F.*)|"
                           "(^\\([^)]*\\)))")
        try:
            result = [s for s in msg_content if regex.match(s)]
            result = list(filter(lambda x: x.strip() != '' and len(x) > 2
                                 and re.match('^(?=.*[A-Za-z]).+$|^(?=.*\\d).+$', x), result))
            try:
                if len(result[0]) < 5:
                    await self.check_chan.send(
                        embed=disnake.Embed(
                            title="Error: Bad Questionnaire Format!",
                            description=f"{msg.author.mention} reformate this -> {msg.jump_url} moron!",
                            color=EmbedPalette.WARNING).set_footer(
                            text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url)
                    )
                    return False
                else:
                    if len(result) == 0:
                        results = []
                        for _ in msg_content:
                            result = list(filter(lambda x: x.strip() != '',
                                                 re.split(f"^" + msg_content[1].replace("|", "\\|"), _)))
                            if len(result) > 0:
                                results.append(result[0])
                        msg_kinks = results[5].strip()
                    else:
                        msg_kinks = result[5].strip()
                    if msg_kinks is None:
                        await self.check_chan.send(
                            embed=disnake.Embed(
                                title="Error: Bad Questionnaire Format!",
                                description=f"{msg.author.mention} reformate this -> {msg.jump_url} moron!",
                                color=EmbedPalette.WARNING).set_footer(
                                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url)
                        )
                        return False
                    else:
                        msg_kinks = msg_kinks.replace('\"', '')
                        return f"{msg_kinks}"
            except Exception as e:
                if len(result) == 0:
                    results = []
                    for _ in msg_content:
                        result = list(filter(lambda x: x.strip() != '',
                                             re.split(f"^" + msg_content[1].replace("|", "\\|"), _)))
                        if len(result) > 0:
                            results.append(result[0])
                    msg_kinks = results[5].strip()
                else:
                    msg_kinks = result[5].strip()
                if msg_kinks is None:
                    await self.check_chan.send(
                        embed=disnake.Embed(
                            title="Error: Bad Questionnaire Format!",
                            description=f"{msg.author.mention} reformate this -> {msg.jump_url} moron!\n||{e}||",
                            color=EmbedPalette.WARNING).set_footer(
                            text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url)
                    )
                    return False
                else:
                    msg_kinks = msg_kinks.replace('\"', '')
                    return f"{msg_kinks}"
        except Exception as e:
            await self.check_chan.send(
                embed=disnake.Embed(
                    title="Error: Bad Questionnaire Format!",
                    description=f"{msg.author.mention} reformate this -> {msg.jump_url} moron!\n||{e}||",
                    color=EmbedPalette.WARNING).set_footer(
                    text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url)
            )
            return False

    async def get_nickname(self, mem_id: int) -> str:
        try:
            member = await self.guild.fetch_member(mem_id)
            return member.display_name
        except Exception as e:
            await self.check_chan.send(embed=disnake.Embed(title="Nickname Error!", description=f"Error: {e}",
                                                           color=0xffd12b).set_footer(
                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))
            return "Error"

    async def to_archive(self, msg: disnake.Message, memid: int):
        chan_msg = msg.content
        files = []
        for file in msg.attachments:
            files.append(await file.to_file())
        if len(chan_msg) >= 1950:
            buffer = io.StringIO(chan_msg)
            files.append(disnake.File(io.BytesIO(buffer.getvalue().encode()), filename="message.txt"))
            archive_msg = await self.archive_chan.send(content=f'Анкету опубликовал {msg.author.mention}',
                                                       files=files)
        else:
            archive_msg = await self.archive_chan.send(content=f'Анкету опубликовал {msg.author.mention}\n{chan_msg}',
                                                       files=files)
        await self.logs_arch_chan.send(
               embed=disnake.Embed(title="Архивация сообщения",
                                   description=f"Анкета пользователя {msg.channel.mention} <@{memid}> заархивирована\n"
                                               f"Ссылка для перехода в архиве: {archive_msg.jump_url}",
                                   color=EmbedPalette.SUCCESS).set_footer(
                     text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))
        await msg.delete()

    async def q_task_save(self):
        self.rp_hist = await self.bot.get_channel(LogData.Q_RP_CHANELL).history(limit=None).flatten()
        self.char_hist = await self.bot.get_channel(LogData.Q_CHAR_CHANELL).history(limit=None).flatten()
        msg_ids = [_[0] for _ in await self.sqlconnect.get_msg_ids()]
        for msg in self.rp_hist:
            if msg.id not in msg_ids:
                mention = await self.mention_slicer(msg.content)
                await self.sqlconnect.save_questionnare(await self.get_nickname(mention),
                                                        mention, msg.id, await self.prefs_slicer(msg))

        for msg in self.char_hist:
            if msg.id not in msg_ids:
                mention = await self.mention_slicer(msg.content)
                await self.sqlconnect.save_questionnare(await self.get_nickname(mention), mention, msg.id,
                                                        await self.prefs_slicer(msg), True)
        await self.logs_chan.send(embed=disnake.Embed(
            title="Сохранение базы данных",
            description=f"База данных успешно сохранена UTC: {datetime.datetime.utcnow()}",
            color=EmbedPalette.SUCCESS)
        )

    async def q_task_check(self):
        q_dict = await self.sqlconnect.get_qs()
        mem_with_role = [_.id for _ in self.guild.get_role(LogData.Q_MEMBER_ROLE).members]
        for qd_item in q_dict.items():
            if qd_item[0] not in mem_with_role:
                await self.sqlconnect.delete_q_by_mem(qd_item[0])
                await self.logs_chan.send(embed=disnake.Embed(
                    title="Удаление ливнувшего/без роли пользователя",
                    description=f"Пользователь <@{qd_item[0]}> был удален из базы данных",
                    color=0x0bffca)
                )
                for q in qd_item[1]:
                    try:
                        if q[1]:
                            msg = await self.char_chan.fetch_message(q[0])
                        else:
                            msg = await self.rp_chan.fetch_message(q[0])
                        await self.to_archive(msg, qd_item[0])
                    except Exception as e:
                        await self.logs_chan.send(embed=disnake.Embed(
                            title="Ошибка при удалении сообщения",
                            description=f"Ошибка: {e}",
                            color=0xff0000)
                        )
        await self.logs_chan.send(embed=disnake.Embed(
            title="Проверка базы данных",
            description=f"База данных успешно проверена UTC: {datetime.datetime.utcnow()}",
            color=EmbedPalette.SUCCESS)
        )

    async def q_task(self):
        while True:
            await self.q_task_save()
            await self.q_task_check()
            await asyncio.sleep(SAVE_DB_TIME)
