# From Solaris: https://github.com/parafoxia/Solaris

import discord
import psutil
import datetime as dt
import typing as t
import common
from platform import python_version
from time import time
from discord.ext import commands

from stenobot.utils import (
    INFO_ICON,
    LOADING_ICON,
    SUCCESS_ICON,
    SUPPORT_GUILD_INVITE_LINK,
    checks,
    chron,
    menu
)

class DetailedServerInfoMenu(menu.MultiPageMenu):
    def __init__(self, ctx, table):
        pagemaps = []
        base_pm = {
            "header": "Information",
            "title": f"Detailed server information for {ctx.guild.name}",
            "thumbnail": ctx.guild.icon_url,
        }

        for key, value in table.items():
            pm = base_pm.copy()
            pm.update({"description": f"Showing {key} information.", "fields": value})
            pagemaps.append(pm)

        super().__init__(ctx, pagemaps, timeout=common.MENU_TIMEOUT2)


class Info(commands.Cog):
    """Commands for retrieving information regarding this bot, from invitation links to detailed bot statistics."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.developer = (await self.bot.application_info()).owner
            self.support_guild = self.bot.get_guild(765626249556262934) # Stenobot
            if self.support_guild is not None:
                #TODO Look up id of helper role. It will be different for each guild.
                self.helper_role = self.support_guild.get_role(765635385316737084) # @helper

            self.bot.ready.up(self) 

    @commands.command(
        name="prefix", 
        help="Displays the bot's prefix in your server. Note that mentioning Solaris will always work."
    )
    async def prefix_command(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        await ctx.send(
            f"{self.bot.info} The {common.BOT_NAME} prefix in this server is {prefix}. To change it, use `{prefix}prefix <new prefix>`."
        )

    @commands.command(
        name="about",
        aliases=["credits"],
        help=f"View information regarding those behind {common.BOT_NAME} development. This includes the developer and the testers, and also shows copyright information.",
    )
    async def about_command(self, ctx):
        prefix = await self.bot.prefix(ctx.guild)
        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                title=f"About {common.BOT_NAME}",
                description=f"Use `{prefix}botinfo` for detailed statistics.",
                thumbnail=self.bot.user.avatar_url,
                fields=[("Developer", self.developer.mention, False)]
            )
        )

    @commands.command(
        name="support", 
        aliases=["sos"], 
        help=f"Provides an invite link to {common.BOT_NAME} support server.")
    async def support_command(self, ctx):
        online = [m for m in self.support_guild.members if not m.bot and m.status == discord.Status.online]
        helpers = [
            m for m in self.support_guild.members if not m.bot and m.top_role.position >= self.helper_role.position
        ]
        online_helpers = set(online) & set(helpers)

        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                description=f"Click [here]({SUPPORT_GUILD_INVITE_LINK}) to join the support server.",
                thumbnail=self.bot.user.avatar_url,
                fields=(
                    ("Online / members", f"{len(online):,} / {len(self.support_guild.members):,}", True),
                    ("Online / helpers", f"{len(online_helpers):,} / {len(helpers):,}", True),
                    ("Developer", str(self.support_guild.owner.status).title(), True),
                ),
            )
        )

    @commands.command(
        name="invite", aliases=["join"], help=f"Provides the links necessary to invite {common.BOT_NAME} to other servers."
    )
    async def invite_command(self, ctx):
        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                thumbnail=self.bot.user.avatar_url,
                fields=(
                    (
                        "Invite",
                        f"To invite {common.BOT_NAME} without administrator privileges, click [here]({self.bot.non_admin_invite}) (you may need to grant {common.BOT_NAME} some extra permissions in order to use some modules).",
                        False,
                    ),
                    ("Servers", f"{self.bot.guild_count:,}", True),
                    ("Users", f"{self.bot.user_count:,}", True)
                ),
            )
        )

    @commands.command(
        name="source", 
        aliases=["src"], 
        help=f"Provides a link to {common.BOT_NAME} source code.")
    async def source_command(self, ctx):
        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                thumbnail=self.bot.user.avatar_url,
                fields=(
                    (
                        "Available under the GPLv3 license",
                        "Click [here](https://github.com/bradykelly/stenobot) to view.",
                        False,
                    ),
                ),
            )
        )

    @commands.command(
        name="issue",
        aliases=["bugreport", "reportbug", "featurerequest", "requestfeature"],
        help=f"Provides a link to open an issue on the {common.BOT_NAME} repo.",
    )
    async def issue_command(self, ctx):
        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                description="If you have discovered a bug not already known or want a feature not requested, open an issue using the green button in the top right of the window.",
                thumbnail=self.bot.user.avatar_url,
                fields=(
                    (
                        # TODO Fix all urls
                        "View all known bugs",
                        "Click [here](https://github.com/bradykelly/stenobot/issues?q=is%3Aopen+is%3Aissue+label%3Abug).",
                        False,
                    ),
                    (
                        "View all planned features",
                        "Click [here](https://github.com/bradykelly/stenobot/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement).",
                        False,
                    ),
                ),
            )
        )

    @commands.command(
        name="changelog",
        aliases=["release"],
        help="Provides a link to view the changelog for the given version. If no version is provided, a general overview is provided.",
    )
    async def changelog_command(self, ctx, version: t.Optional[str]):
        url = (
            "https://github.com/bradykelly/stenobot/releases"
            if not version
            else f"https://github.com/bradykelly/stenobot/releases/tag/v{version}"
        )
        version_info = f"version {version}" if version else "all versions"
        await ctx.send(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                description=f"Click [here]({url}) to information on {version_info}.",
                thumbnail=self.bot.user.avatar_url,
            )
        )

    @commands.command(name="ping", help=f"Pings {common.BOT_NAME}.")
    async def ping_command(self, ctx):
        lat = self.bot.latency * 1000
        s = time()
        pm = await ctx.send(f"{self.bot.info} Pong! DWSP latency: {lat:,.0f} ms. Response time: - ms.")
        e = time()
        await pm.edit(
            content=f"{self.bot.info} Pong! DWSP latency: {lat:,.0f} ms. Response time: {(e-s)*1000:,.0f} ms."
        )

    @commands.command(
        name="botinfo",
        aliases=["bi", "botstats", "stats", "bs"],
        cooldown_after_parsing=True,
        help=f"Displays statistical information on {common.BOT_NAME}. This includes process and composition information, and also includes information about {common.BOT_NAME} reach.",
    )
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def botinfo_command(self, ctx):
        with (proc := psutil.Process()).oneshot():
            prefix = await self.bot.prefix(ctx.guild)
            uptime = time() - proc.create_time()
            cpu_times = proc.cpu_times()
            total_memory = psutil.virtual_memory().total / (1024 ** 2)
            memory_percent = proc.memory_percent()
            memory_usage = total_memory * (memory_percent / 100)

            await ctx.send(
                embed=self.bot.embed.build(
                    ctx=ctx,
                    header="Information",
                    title="Bot information",
                    description=f"{common.BOT_NAME} was developed by {(await self.bot.application_info()).owner.mention}. Use `{prefix}about` for more information.",
                    thumbnail=self.bot.user.avatar_url,
                    fields=(
                        ("Bot version", f"{self.bot.version}", True),
                        ("Python version", f"{python_version()}", True),
                        ("discord.py version", f"{discord.__version__}", True),
                        ("Uptime", chron.short_delta(dt.timedelta(seconds=uptime)), True),
                        (
                            "CPU time",
                            chron.short_delta(
                                dt.timedelta(seconds=cpu_times.system + cpu_times.user), milliseconds=True
                            ),
                            True,
                        ),
                        (
                            "Memory usage",
                            f"{memory_usage:,.3f} / {total_memory:,.0f} MiB ({memory_percent:.0f}%)",
                            True,
                        ),
                        ("Servers", f"{self.bot.guild_count:,}", True),
                        ("Users", f"{self.bot.user_count:,}", True),
                        ("Commands", f"{self.bot.command_count:,}", True),
                        ("Code", f"{self.bot.loc.code:,} lines", True),
                        ("Comments", f"{self.bot.loc.docs:,} lines", True),
                        ("Blank", f"{self.bot.loc.empty:,} lines", True),
                        (
                            "Database calls since uptime",
                            f"{self.bot.db._calls:,} ({self.bot.db._calls/uptime:,.3f} per second)",
                            True,
                        ),
                    ),
                )
            )

    #TODO New 'Leave' command, without cleanup blah blah.

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_command(self, ctx):
        # Use hub shutdown instead where possible.
        await ctx.message.delete()
        await self.bot.shutdown()


def setup(bot):
    bot.add_cog(Info(bot))
