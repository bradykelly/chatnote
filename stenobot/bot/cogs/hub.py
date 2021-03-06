# From Solaris: https://github.com/parafoxia/Solaris

import common
from stenobot.config import Config
from discord.ext import commands


class Hub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #TODO Stuff when the bot isn't in any guild when it connects.
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.guild = self.bot.get_guild(Config.HUB_GUILD_ID)

            if self.guild is not None:
                self.commands_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
                self.relay_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
                self.stdout_channel = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)

                if self.stdout_channel is not None:
                    await self.stdout_channel.send(
                        f"{self.bot.info} {common.BOT_NAME} is now online! (Version {self.bot.version})"
                    )

            self.bot.ready.up(self)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.db.execute("INSERT OR IGNORE INTO guild_config (GuildID) VALUES (?)", guild.id)

        if self.stdout_channel is not None:
            await self.stdout_channel.send(
                f"{self.bot.info} Joined guild! Nº: {self.bot.guild_count:,} • Name: {guild.name} • Members: {guild.member_count:,} • ID: {guild.id}"
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db.execute("DELETE FROM guild_config WHERE GuildID = ?", guild.id)

        if self.stdout_channel is not None:
            await self.stdout_channel.send(
                f"{self.bot.info} Left guild. Name: {guild.name} • Members: {guild.member_count:,} • ID: {guild.id}"
            )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if self.bot.ready.booted:
            if msg.guild == self.guild and not msg.author.bot and self.bot.user in msg.mentions:
                if msg.channel == self.commands_channel:
                    if msg.content.startswith("shutdown"):
                        await self.bot.shutdown()

                elif msg.channel == self.relay_channel:
                    # TODO: Add relay system.
                    pass


def setup(bot):
    bot.add_cog(Hub(bot))
