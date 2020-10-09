# From Solaris: https://github.com/parafoxia/Solaris

import typing as t
import discord
import common
from discord.ext import commands
from chatnotebot.utils import ERROR_ICON, LOADING_ICON, SUCCESS_ICON, checks, menu, modules


class SetupMenu(menu.SelectionMenu):
    def __init__(self, ctx):
        pagemap = {
            "header": "Setup Wizard",
            "title": "Hello!",
            "description": f"Welcome to the {common.BOT_NAME} first time setup! You need to run this before you can use most of {common.BOT_NAME}' commands, but you only ever need to run once.\n\nIn order to operate effectively in your server, {common.BOT_NAME} needs to create a few things:",
            "thumbnail": ctx.bot.user.avatar_url,
            "fields": (
                (
                    "A log channel",
                    f"This will be called {common.BOT_NAME}-logs and will be placed directly under the channel you run the setup in. This channel is what {common.BOT_NAME} will use to communicate important information to you, so it is recommended you only allow server moderators access to it. You will be able to change what {common.BOT_NAME} uses as the log channel later.",
                    False,
                ),
                (
                    "An admin role",
                    f"This will be called {common.BOT_NAME} Administrator and will be placed at the bottom of the role hierarchy. This role does not provide members any additional access to the server, but does allow them to use {common.BOT_NAME}' configuration commands. Server administrators do not need this role to configure {common.BOT_NAME}. You will be able to change what {common.BOT_NAME} uses as the admin role later.",
                    False,
                ),
                (
                    "Ready?",
                    f"If you are ready to run the setup, select {ctx.bot.tick}. To exit the setup without changing anything select {ctx.bot.cross}.",
                    False,
                ),
            ),
        }
        super().__init__(ctx, ["confirm", "cancel"], pagemap, timeout=120.0)

    async def start(self):
        r = await super().start()

        if r == "confirm":
            pagemap = {
                "header": "Setup Wizard",
                "description": "Please wait... This should only take a few seconds.",
                "thumbnail": LOADING_ICON,
            }
            await self.switch(pagemap, clear_reactions=True)
            await self.run()
        elif r == "cancel":
            await self.stop()

    async def run(self):
        lc = None
        if not await modules.retrieve.system__logchannel(self.bot, self.ctx.guild):
            if self.ctx.guild.me.guild_permissions.manage_channels:
                lc = await self.ctx.guild.create_text_channel(
                    name=f"{common.BOT_NAME}-logs",
                    category=self.ctx.channel.category,
                    position=self.ctx.channel.position,
                    topic=f"Log output for {self.ctx.guild.me.mention}",
                    reason=f"Needed for {common.BOT_NAME} log output.",
                )
                await self.bot.db.execute(
                    "UPDATE guild_config SET DefaultLogChannelID = ?, LogChannelID = ? WHERE GuildID = ?",
                    lc.id,
                    lc.id,
                    self.ctx.guild.id,
                )
                await lc.send(f"{self.bot.tick} The log channel has been created and set to {lc.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": f"The log channel could not be created as {common.BOT_NAME} does not have the Manage Channels permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await self.switch(pagemap)
                return

        if not await modules.retrieve.system__adminrole(self.bot, self.ctx.guild):
            if self.ctx.guild.me.guild_permissions.manage_roles:
                ar = await self.ctx.guild.create_role(
                    name="{common.BOT_NAME} Administrator",
                    permissions=discord.Permissions(permissions=0),
                    reason=f"Needed for {common.BOT_NAME} configuration.",
                )
                await self.bot.db.execute(
                    "UPDATE guild_config SET DefaultAdminRoleID = ?, AdminRoleID = ? WHERE GuildID = ?",
                    ar.id,
                    ar.id,
                    self.ctx.guild.id,
                )
                await lc.send(f"{self.bot.tick} The admin role has been created and set to {ar.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": f"The admin role could not be created as {common.BOT_NAME} does not have the Manage Roles permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await self.switch(pagemap)
                return

        await self.complete()

    async def configure_modules(self):
        await self.complete()

    async def complete(self):
        pagemap = {
            "header": "Setup",
            "title": "First time setup complete",
            "description": f"Congratulations - the first time setup has been completed! You can now use all of {common.BOT_NAME}' commands, and activate all of {common.BOT_NAME}' modules.\n\nEnjoy using {common.BOT_NAME}!",
            "thumbnail": SUCCESS_ICON,
        }
        await modules.config._system__runfts(self.bot, self.ctx.channel, 1)
        await self.switch(pagemap, clear_reactions=True)


class Modules(commands.Cog):
    """Configure, activate, and deactivate {common.BOT_NAME} modules."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    @commands.command(name="setup", help="Runs the first time setup.")
    @checks.bot_has_booted()
    @checks.first_time_setup_has_not_run()
    @checks.author_can_configure()
    @checks.guild_is_not_discord_bot_list()
    async def setup_command(self, ctx):
        await SetupMenu(ctx).start()

    @commands.command(
        name="config", aliases=["set"], help=f"Configures {common.BOT_NAME}; use `help config` to bring up a special help menu."
    )
    @checks.bot_has_booted()
    @checks.first_time_setup_has_run()
    @checks.author_can_configure()
    async def config_command(
        self,
        ctx,
        module: str,
        attr: str,
        objects: commands.Greedy[t.Union[discord.TextChannel, discord.Role]],
        *,
        text: t.Optional[t.Union[int, str]],
    ):
        if module.startswith("_") or attr.startswith("_"):
            await ctx.send(f"{self.bot.cross} The module or attribute you are trying to access is non-configurable.")
        elif (func := getattr(modules.config, f"{module}__{attr}", None)) is not None:
            await func(self.bot, ctx.channel, (objects[0] if len(objects) == 1 else objects) or text)
        else:
            await ctx.send(f"{self.bot.cross} Invalid module or attribute.")

    @commands.command(
        name="retrieve",
        aliases=["get"],
        help="Retrieves attribute information for a module. Note that the output is raw, so some attributes may appear to have strange or incorrect values when in reality they are fine.",
    )
    @checks.bot_has_booted()
    @checks.first_time_setup_has_run()
    @checks.author_can_configure()
    async def retrieve_command(self, ctx, module: str, attr: str):
        if module.startswith("_") or attr.startswith("_"):
            await ctx.send(f"{self.bot.cross} The module or attribute you are trying to access is non-configurable.")
        elif (func := getattr(modules.retrieve, f"{module}__{attr}", None)) is not None:
            v = await func(self.bot, ctx.guild)
            value = getattr(v, "mention", v)
            await ctx.send(f"{self.bot.info} Value of {attr}: {value}")
        else:
            await ctx.send(f"{self.bot.cross} Invalid module or attribute.")

    @commands.command(name="activate", aliases=["enable"], help="Activates a module.")
    @checks.bot_is_ready()
    @checks.log_channel_is_set()
    @checks.first_time_setup_has_run()
    @checks.author_can_configure()
    async def activate_command(self, ctx, module: str):
        if module.startswith("_"):
            await ctx.send(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (func := getattr(modules.activate, module, None)) is not None:
            await func(ctx)
        else:
            await ctx.send(f"{self.bot.cross} That module either does not exist, or can not be activated.")

    @commands.command(name="deactivate", aliases=["disable"], help="Deactivates a module.")
    @checks.bot_is_ready()
    @checks.log_channel_is_set()
    @checks.first_time_setup_has_run()
    @checks.author_can_configure()
    async def deactivate_command(self, ctx, module: str):
        if module.startswith("_"):
            await ctx.send(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (func := getattr(modules.deactivate, module, None)) is not None:
            await func(ctx)
        else:
            await ctx.send(f"{self.bot.cross} That module either does not exist, or can not be deactivated.")

    @commands.command(
        name="restart", help="Restarts a module. This is a shortcut command which calls `deactivate` then `activate`."
    )
    @checks.bot_is_ready()
    @checks.log_channel_is_set()
    @checks.first_time_setup_has_run()
    @checks.author_can_configure()
    async def restart_command(self, ctx, module: str):
        if module.startswith("_"):
            await ctx.send(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (dfunc := getattr(modules.deactivate, module, None)) is not None and (
            afunc := getattr(modules.activate, module, None)
        ) is not None:
            await dfunc(ctx)
            await afunc(ctx)
        else:
            await ctx.send(f"{self.bot.cross} That module either does not exist, or can not be restarted.")


def setup(bot):
    bot.add_cog(Modules(bot))
