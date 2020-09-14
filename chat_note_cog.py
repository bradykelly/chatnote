
import discord
import common
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cog import Cog

class ChatNoteCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    def format_usage(self, ctx):
        '''
        Contructs a formatted usage string for a command.
        '''
        usg = f"{self.bot.command_prefix}{ctx.command.name} {ctx.command.usage}"
        return usg

    async def show_message_embed(self, ctx, message, title=None):
        '''
        Shows the user information in an embed
        '''
        if title is None:
            title = f"Command Output"
        em = discord.Embed(title=title, description="```\n" + message + "\n```", colour=0xBD362F)
        em.set_footer(text="ChatNote (c) 2020 Erisia")
        em.timestamp = datetime.utcnow()
        await ctx.send(embed=em)

    async def show_message_codeblock(self, ctx, message, title=None):
        '''
        Shows the user a message in the format of a code block
        '''
        msg = "```\n"
        if title is not None:
            msg += title + "\n\n"
        msg += message
        msg += "\n```"
        await ctx.send(msg)

    @Cog.listener()
    async def on_ready(self):
        '''
        Prints details of a new Discord connection
        '''
        print(f"{self.bot.user} ({self.bot.user.id}) has connected to Discord! In " + str(self.get_guild_count()) + " guild(s).")  

    @commands.command(
        help="Show the About info for this bot",
        brief="Show About info",
        name="about"
    )
    async def show_about(self, ctx):
        '''
        Shows the about info for this bot
        '''     
        with open("about.txt", "r") as f:
            about = f.read()
            if about is not None:
                about = about.strip()
            else:
                about = "No help text was found on file"
            await self.show_message_codeblock(ctx, about, f"About {common.BOT_NAME}")