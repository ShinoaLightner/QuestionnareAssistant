import mysql.connector
import sqlite3
import LogData
import datetime
import disnake
from disnake.ext import commands
import EmbedPalette


class SQLDB:
    def __init__(self, bot: commands.Bot, host: str = LogData.HOST, user: str = LogData.USER,
                 password: str = LogData.PASSWORD, database: str = LogData.DATABASE):
        self.bot = bot
        self.logs_chan = None
        self.sqlconnect = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.sqlconnect.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")

    async def get_chan(self):
        self.logs_chan = self.bot.get_channel(LogData.Q_LOG_CHANELL)

    async def q_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM qList")
        return self.cursor.fetchone()[0]

    async def get_msg_ids(self, mem_id: int = None):
        if mem_id is None:
            self.cursor.execute("SELECT msgID FROM qList")
        else:
            self.cursor.execute(f"SELECT msgID FROM qList WHERE mem_id={mem_id}")
        return self.cursor.fetchall()

    async def get_qs(self) -> dict:
        self.cursor.execute("SELECT memID FROM qList")
        q_list = self.cursor.fetchall()
        mem_id_set = set([_[0] for _ in q_list])
        q_dict = {}
        for memID in mem_id_set:
            self.cursor.execute(f"SELECT msgID, isChara FROM qList WHERE memID={memID}")
            q_dict[memID] = self.cursor.fetchall()
        return q_dict

    async def save_questionnare(self, nickname: str, mem_id: int, msg_id: int, prefs: str or bool,
                                is_chara: bool = False):
        try:
            self.cursor.execute("INSERT INTO qList (nickname, memID, msgID, isChara) "
                                f"VALUES (\"{nickname}\", {mem_id}, {msg_id}, {is_chara})")
            if prefs:
                self.cursor.execute("INSERT INTO qKinks (msgID, kinkStr, isChara) "
                                    f"VALUES ({msg_id}, \"{prefs}\", {is_chara})")
            else:
                self.cursor.execute(f"INSERT INTO qKinks (msg_id, isChara) VALUES ({msg_id}, {is_chara})")
            self.sqlconnect.commit()
        except Exception as e:
            self.sqlconnect.rollback()
            await self.logs_chan.send(embed=disnake.Embed(title="Database Error!", description=f"Error: {e}",
                                                          color=EmbedPalette.IMPORTANT).set_footer(
                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))

    async def check_questionnare(self, mem_id: int):
        self.cursor.execute(f"SELECT msgID FROM qList WHERE memID = {mem_id};")
        self.cursor.fetchone()

    async def delete_q_by_mem(self, mem_id: int):
        try:
            self.cursor.execute(f"SELECT msgID FROM qList WHERE memID = {mem_id}")
            msg_id = self.cursor.fetchall()
            self.cursor.execute(f"DELETE FROM qList WHERE memID = {mem_id}")
            for msg in msg_id:
                self.cursor.execute(f"DELETE FROM qKinks WHERE msgID = {msg[0]}")
            self.sqlconnect.commit()
        except Exception as e:
            self.sqlconnect.rollback()
            await self.logs_chan.send(embed=disnake.Embed(title="Database Error!", description=f"Error: {e}",
                                                          color=EmbedPalette.IMPORTANT).set_footer(
                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))

    async def delete_q_by_msg(self, msg_id: int):
        try:
            self.cursor.execute(f"DELETE FROM qList WHERE msgID={msg_id}")
            self.cursor.execute(f"DELETE FROM qKinks WHERE msgID={msg_id}")
            self.sqlconnect.commit()
        except Exception as e:
            self.sqlconnect.rollback()
            await self.logs_chan.send(embed=disnake.Embed(title="Database Error!", description=f"Error: {e}",
                                                          color=EmbedPalette.IMPORTANT).set_footer(
                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))

    async def update_kinks(self, msg_id: int, prefs: str or bool):
        try:
            self.cursor.execute(f"UPDATE qKinks SET kinkStr = \"{prefs}\" WHERE msgID = {msg_id}")
            self.sqlconnect.commit()
        except Exception as e:
            self.sqlconnect.rollback()
            await self.logs_chan.send(embed=disnake.Embed(title="Database Error!", description=f"Error: {e}",
                                                          color=EmbedPalette.IMPORTANT).set_footer(
                text=f"UTC Time: {datetime.datetime.now()}", icon_url=self.bot.user.avatar.url))
