# From Solaris: TODO Get correct url

import datetime as dt
import typing as t
from collections import defaultdict
from discord.ext import commands
from discord.ext.commands.cog import Cog
from lib.utils import checks, chron, menu, modules, string

class HelpMenu(menu.MultiPageMenu):
    def __init__(self, ctx, pagemaps):
        super().__init__(ctx, pagemaps, timeout=120.0)

class ConfigHelpMenu(menu.NumberedSelectionMenu):
    def __init__(self, ctx):
        pagemap = {
            "header": "Help",
            "title": "Configuration help",
            "description": "Select the module you want to configure.",
            "thumbnail": ctx.bot.user.avatar_url,
        }
        super().__init__(
            ctx,
            [cog.qualified_name.lower() for cog in ctx.bot.cogs.values() if getattr(cog, "configurable", False)],
            pagemap,
        )

    async def start(self):
        if (r := await super().start()) is not None:
            await self.display_help(r)

    async def display_help(self, module):
        prefix = await self.bot.prefix(self.ctx.guild)

        await self.message.clear_reactions()
        await self.message.edit(
            embed=self.bot.embed.build(
                ctx=self.ctx,
                header="Help",
                title=f"Configuration help for {module}",
                description=(
                    list(filter(lambda c: c.qualified_name.lower() == module, self.bot.cogs.values())).pop().__doc__
                ),
                thumbnail=self.bot.user.avatar_url,
                fields=(
                    (
                        (doc := func.__doc__.split("\n", maxsplit=1))[0],
                        f"{doc[1]}\n`{prefix}config {module} {name[len(module)+2:]}`",
                        False,
                    )
                    for name, func in filter(lambda f: module in f[0], modules.config.__dict__.items())
                    if not name.startswith("_")
                ),
            )
        )        

class Help(commands.Cog):
    """Assistance with using a configuring ChatNoteBot."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")  

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help") 

    @staticmethod
    async def basic_syntax(ctx, cmd, prefix):
        try:
            await cmd.can_run(ctx)
            return f"{prefix}{cmd.name}" if cmd.parent is None else f"  ↳ {cmd.name}"
        except commands.CommandError:
            return f"{prefix}{cmd.name} (✗)" if cmd.parent is None else f"  ↳ {cmd.name} (✗)"

    @staticmethod
    def full_syntax(ctx, cmd, prefix):
        invokations = "|".join([cmd.name, *cmd.aliases])
        if (p := cmd.parent) is None:
            return f"```{prefix}{invokations} {cmd.signature}```"
        else:
            p_invokations = "|".join([p.name, *p.aliases])
            return f"```{prefix}{p_invokations} {invokations} {cmd.signature}```"                         

    @staticmethod
    async def required_permissions(ctx, cmd):
        try:
            await cmd.can_run(ctx)
            return "Yes"
        except commands.MissingPermissions as exc:
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms])
            return f"No - You are missing the {mp} permission(s)"
        except commands.BotMissingPermissions as exc:
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms])
            return f"No - Solaris is missing the {mp} permission(s)"
        except checks.AuthorCanNotConfigure:
            return "No - You are not able to configure Solaris"
        except commands.CommandError:
            return "No - Solaris is not configured properly"

    async def get_command_mapping(self, ctx):
        mapping = defaultdict(list)

        for cog in self.bot.cogs.values():
            if cog.__doc__ is not None:
                for cmd in cog.walk_commands():
                    if cmd.help is not None:
                        mapping[cog].append(cmd)
        return mapping

    @commands.command(
        name="help",
        help="Help with anything Solaris. Passing a command name or alias through will show help with that specific command, while passing no arguments will bring up a general command overview.",
    )
    async def help_command(self, ctx, *, cmd: t.Optional[t.Union[converters.Command, str]]):
        prefix = await self.bot.prefix(ctx.guild)

        if isinstance(cmd, str):
            await ctx.send(f"{self.bot.cross} Solaris has no commands or aliases with that name.")

        elif isinstance(cmd, commands.Command):
            if cmd.name == "config":
                await ConfigHelpMenu(ctx).start()
            else:
                await ctx.send(
                    embed=self.bot.embed.build(
                        ctx=ctx,
                        header="Help",
                        description=cmd.help,
                        thumbnail=self.bot.user.avatar_url,
                        fields=(
                            ("Syntax (<required> • [optional])", self.full_syntax(ctx, cmd, prefix), False),
                            (
                                "On cooldown?",
                                f"Yes, for {chron.long_delta(dt.timedelta(seconds=s))}."
                                if (s := cmd.get_cooldown_retry_after(ctx))
                                else "No",
                                False,
                            ),
                            ("Can be run?", await self.required_permissions(ctx, cmd), False),
                            (
                                "Parent",
                                self.full_syntax(ctx, p, prefix) if (p := cmd.parent) is not None else "None",
                                False,
                            ),
                        ),
                    )
                )

        else:
            pagemaps = []

            for cog, cmds in (await self.get_command_mapping(ctx)).items():
                pagemaps.append(
                    {
                        "header": "Help",
                        "title": f"The `{cog.qualified_name.lower()}` module",
                        "description": f"{cog.__doc__}\n\nUse `{prefix}help [command]` for more detailed help on a command. You can not run commands with `(✗)` next to them.",
                        "thumbnail": self.bot.user.avatar_url,
                        "fields": (
                            (
                                f"{len(cmds)} command(s)",
                                "```{}```".format(
                                    "\n".join([await self.basic_syntax(ctx, cmd, prefix) for cmd in cmds])
                                ),
                                False,
                            ),
                        ),
                    }
                )

            await HelpMenu(ctx, pagemaps).start()        