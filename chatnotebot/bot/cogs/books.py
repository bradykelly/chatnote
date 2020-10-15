from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument
from discord.ext import commands
from chatnotebot.bot.chatnote_base_cog import ChatNoteBaseCog
from chatnotebot.utils.synchronise import Synchronise

BOOKS_COMMANDS = ["list", "open", "del"]

class Books(ChatNoteBaseCog, name="book"):
    """Commands to manage your ChatNote notebooks"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            #await Synchronise(self.bot).on_boot()
            self.bot.ready.up(self)      

    # 'books' command group
    @commands.group(
        name="books",
        aliases = ["book", "notebook", "notebooks"],
        title="Commands to help you manage your ChatNote notebooks",
        help="List or delete notebooks.",
        brief="Manage your notebooks",
        usage= f"[list | del]"
    )
    async def books(self, ctx):
        if ctx.invoked_subcommand is None or (ctx.invoked_subcommand is not None and ctx.invoked_subcommand.name not in BOOKS_COMMANDS):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    @books.error
    async def books_handler(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")       

    @books.command(
        name="open",
        aliases = ["choose", "set"], 
        help="Sets which notebook is currently in use. The default is Main."
    )
    async def open_command(self, ctx, name):{

    }

    @books.command(
        name="list",
        alias=["show", "all"],
        help="List all your notebooks",
        brief="List notebooks"
    )           
    async def list(self, ctx):          
        books = await self.bot.db.get_books(ctx.message.author.id)
        book_count = 0
        list_text = ""
        for book in books:   
            msg = f"{str(book[0]).zfill(6)}:   {book[1]}"
            list_text += msg + "\n"
            book_count += 1
        list_text += "\n" + f"{book_count} notebook(s)"
        await self.show_message_codeblock(ctx, list_text, f"Notebooks")

    @list.error
    async def list_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")

    # 'del' command
    @books.command(
        name="del",
        aliases=["delete"],        
        help="Delete a notebook. i.e. Delete all notes in the notebook",
        brief="Delete a notebook",
        usage="<name>: Name of the notebook to delete"
    )
    async def del_book(self, ctx, name):
        count = await self.bot.db.del_book(ctx.message.author.id, name)

        if count > 0:
            await self.show_message_codeblock(ctx, f"Notebook '{name}' deleted' ", "Delete Noteboook")
        else:
            await self.show_message_codeblock(ctx, f"Notebook :'{name}' doesn't exist", "Delete Noteboook")

    @del_book.error
    async def del_book_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await self.show_message_codeblock(ctx, self.format_usage(ctx), "Usage")          


def setup(bot):
    bot.add_cog(Books(bot))            