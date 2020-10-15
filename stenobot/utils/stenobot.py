import common
import sys
from datetime import datetime
from discord import commands
from stenobot.models.note import Note

class Stenobot():
    def __init__(self, bot):
        self.bot = bot

    async def get_open_book(self, guildId, userId):
        try:
            return self.bot.db.field("SELECT open_notebook FROM members WHERE guildId = ? and userId = ?", (guildId, userId))
        except:
            print("Stenobot class: " + sys.exc_info()[0])
            raise            
    
    async def set_open_book(self, guildId, userId, name):
        book = await self.get_open_book(guildId, userId)
        try:
            if (book is not None):
                self.bot.db.execute("UPDATE members SET open_book = ? WHERE guildId = ? and userId = ?", (name, guildId, userId))
            else:
                self.bot.db.execute("INSERT INTO members (guildId, userId, open_book) VALUES (?, ?, ?)", (guildId, userId, name))
        except:
            print("Stenobot class: " + sys.exc_info()[0])
            raise

    async def insert_note(self, guildId, userId, text):  
        notebook = await self.get_open_book() 
        if (notebook := self.get_open_book(guildId, userId)) is None:
            notebook = common.DEFAULT_NOTEBOOK
        insert_sql = "INSERT INTO 'notes' ('Time', 'UserId', 'Notebook', 'Text') VALUES(?, ?, ?, ?);"
        values = (datetime.now(), userId, notebook.strip().lower(), text)
        cur = None
        try:
            cur = await self.bot.db.execute(insert_sql, values)
            return cur.rowcount
        except:
            print("Stenobot class: " + sys.exc_info()[0])
            raise    

    async def get_notes(self, guildId, userId, notebook=None):
        if notebook is None:
            if (notebook := self.get_open_book(guildId, userId)) is None:
                notebook = common.DEFAULT_NOTEBOOK
        select_sql = "SELECT Id, Time, Text FROM notes WHERE UserId = ? and Notebook = ?;"
        values = (userId, notebook.strip().lower())
        try:
            rows = await self.bot.db.records(select_sql, values)
            notes = []
            for row in rows:
                notes.append(Note(row[0], row[1], row[2]))
            return notes
        except Exception as ex:
            print("Stenobot class: " + sys.exc_info()[0])
            raise 
        
    async def delete_note(self, userId, noteId):
        del_sql = "DELETE FROM notes WHERE UserId = ? AND Id = ?"
        values = (userId, noteId)
        try:
            await self.bot.db.execute(del_sql, values)
        except Exception as ex:
            print("Stenobot class: " + sys.exc_info()[0])
            raise        