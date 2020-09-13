import discord
import dal
from datetime import datetime
from discord.ext.commands.cog import Cog
from discord.ext.commands.errors import MissingRequiredArgument
from discord.ext import commands

class NoteCommands(Cog, name="NoteCommands"):
    
    def __init__(self, bot):
        self.bot = bot
    
    def get_guild_count(self):
        guild_count = 0
        for guild in self.bot.guilds:
            guild_count += 1
        return guild_count

    async def show_message_embed(self, ctx: commands.Context, message, title=None):
        if title is None:
            title = "Command Feedback"
        em = discord.Embed(title=title, description=message, colour=0xBD362F)
        #em.set_footer("ChatNote (c) 2020 Erisia")
        em.timestamp = datetime.utcnow()
        await ctx.send(embed=em)

    @Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} ({self.bot.user.id}) has connected to Discord! In " + str(self.get_guild_count()) + " guild(s).")  

    # 'note' command group
    @commands.group(
        help="Commands to help you manage your ChatNote notebook",
        brief="Use your notebook",
        usage=f"[add | find | list | del] [text]: Default is 'add'. For add, 'text' is required"
    )
    async def note(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.channel.send("First layer")

    # Add command
    @note.command(
        help="Add <text-to-add> to your current notebook, or a named notebook",
        brief="Add text to a notebook",
        usage="[notebook-name] <text-to-add>: Notebook-name (optional) must be a single word"
    )
    async def add(self, ctx, text=None, notebook=None):
        if (notebook is not None):
            notebook = notebook.strip()        
        if text is not None:
            text = text.strip() 
        dal.insert_note(ctx.message.author.id, text, notebook) 
        await self.show_message_embed(ctx.channel, r"note added: " + text)

    @add.error
    async def add_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument) and error.param.name == "text":
            await ctx.channel.send(f"Usage: {self.bot.command_prefix}note add <text-to-add>")

    # List command
    @note.command(
        help="List all notes in your current notebook, or a named notebook",
        brief="List all notes",
        usage="[notebook-name]: Notebook-name (optional) must be a single word"
    )
    async def list(self, ctx, notebook=None):
        if (notebook is None):
            notebook = dal.DEFAULT_NOTEBOOK
        notebook = notebook.strip() 
        notes = dal.get_notes(ctx.message.author.id, notebook)
        note_count = 0
        for note in notes:            
            await ctx.channel.send(f"{str(note.id).zfill(6)}:   {note.time[:19]}   {note.text}")
            note_count += 1
        await ctx.channel.send(f"{note_count} note(s) in '{notebook}'")

    # del command
    @note.command(
        help="Delete a note from your notebooks",
        brief="Delete note",
        usage="<note_id>: Id of the note to delete. Required",
        name="del"
    )
    async def delnote(self, ctx, note_id):
        del_id = int(note_id)

    @delnote.error
    async def delnote_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument) and error.param.name == "note_id":
            usage = f"Usage: {self.bot.command_prefix}note del <note_id>"
            await ctx.channel.send(usage)

    # leave command
    @commands.command(
        hidden=True
    )
    async def leave(self, ctx):
        server = ctx.message.server
        channel = ctx.message.author.channel
        await channel.leave()

    @Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"{self.bot.user.name} was removed from guild {guild.name}")