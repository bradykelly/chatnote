import os
from notes_cog import NoteCommands
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
BOT_NAME = "ChatNoteBot"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
note_args = ["add", "find", "list", "del"]

bot = commands.Bot(command_prefix="##", case_insensitive=True, name=BOT_NAME, description="A note taking bot")

bot.add_cog(NoteCommands(bot))
bot.help_command.cog = bot.cogs["NoteCommands"]

bot.run(DISCORD_TOKEN)
