#From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/modules/activate.py

import common
from chatnotebot.utils.modules import retrieve

async def gateway(ctx):
    async with ctx.typing():
        active, rc_id, br_id, gt = (
            await ctx.bot.db.record(
                "SELECT active, rules_channel_id, blocking_role_id, gate_text FROM gateway WHERE guildId = ?", ctx.guild.id
            )
            or [None] * 4
        )

        if active:
            await ctx.send(f"{ctx.bot.cross} The gateway module is already active.")
        elif not (ctx.guild.me.guild_permissions.manage_roles and ctx.guild.me.guild_permissions.kick_members):
            await ctx.send(
                f"{ctx.bot.cross} The gateway module could not be activated as {common.BOT_NAME} does not have the Manage Roles and Kick Members permissions."
            )
        elif (rc := ctx.bot.get_channel(rc_id)) is None:
            await ctx.send(
                f"{ctx.bot.cross} The gateway module could not be activated as the rules channel does not exist or can not be accessed by {common.BOT_NAME}."
            )
        elif ctx.guild.get_role(br_id) is None:
            await ctx.send(
                f"{ctx.bot.cross} The gateway module could not be activated as the blocking role does not exist or can not be accessed by {common.BOT_NAME}."
            )
        else:
            gm = await rc.send(
                gt
                or f"**Attention:** Do you accept the rules outlined above? If you do, select {ctx.bot.emoji.mention('confirm')}, otherwise select {ctx.bot.emoji.mention('cancel')}."
            )
            for emoji in ctx.bot.emoji.get_many("confirm", "cancel"):
                await gm.add_reaction(emoji)

            await ctx.bot.db.execute(
                "UPDATE gateway SET Active = 1, GateMessageID = ? WHERE guildId = ?", gm.id, ctx.guild.id
            )
            await ctx.send(f"{ctx.bot.tick} The gateway module has been activated.")
            lc = await retrieve.log_channel(ctx.bot, ctx.guild)
            await lc.send(f"{ctx.bot.info} The gateway module has been activated.")