# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/modules/config.py

import discord
from ...utils import string
from ..modules import retrieve
from ....common import common

MAX_PREFIX_LEN = 5

MAX_MEMBER_ROLES = 3
MAX_EXCEPTION_ROLES = 3
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MAX_GATETEXT_LEN = 250
MAX_WGTEXT_LEN = 1000
MAX_WGBOTTEXT_LEN = 500

MIN_POINTS = 5
MAX_POINTS = 99
MIN_STRIKES = 1
MAX_STRIKES = 9

async def _system__runfts(bot, channel, value):
    await bot.db.execute("UPDATE guild_config SET run_fts = ? WHERE guildId = ?", value, channel.guild.id)

async def system__prefix(bot, channel, values):
    """The server prefix
    The prefix ChatNoteBot responds to, aside from mentions. The default is >>."""
    for pfx in values:
        if not isinstance(pfx, str):
            await channel.send(f"{bot.cross} A server prefix must be a string.")
        elif len(pfx) > MAX_PREFIX_LEN:
            await channel.send(
                f"{bot.cross} A server prefix must be no longer than {MAX_PREFIX_LEN} characters in length."
        )
    else:
        prefString = common.CSV_SEPARATOR.join(values)
        await bot.db.execute("UPDATE guild_config SET command_prefixes = ? WHERE guildId = ?", prefString, channel.guild.id)
        await channel.send(f"{bot.tick} The server prefixes have been set to {prefString}.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The server prefixes have been set to {prefString}.")    

async def system__logchannel(bot, channel, value):
    """The log channel
    The channel ChatNoteBot uses to communicate important information. It is recommended you keep this channel restricted to members of the server's moderation team. Upon selecting a new channel, ChatNoteBot will delete the one that was created during the first time setup should it still exist."""
    if not isinstance(value, discord.TextChannel):
        await channel.send(f"{bot.cross} The log channel must be a Discord text channel in this server.")
    elif not value.permissions_for(channel.guild.me).send_messages:
        await channel.send(f"{bot.cross} The given channel can not be used as the log channel as ChatNoteBot can not send messages to it.")
    else:
        await bot.db.execute("UPDATE guild_config SET log_channel_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(f"{bot.tick} The log channel has been set to {value.mention}.")
        await value.send(
            (
                f"{bot.info} This is the new log channel. ChatNoteBot will use this channel to communicate with you if needed. "
                "Configuration updates will also be sent here."
            )
        )

        if (
            channel.guild.me.guild_permissions.manage_channels
            and (dlc := await retrieve.system__defaultlogchannel(bot, channel.guild)) is not None
        ):
            await dlc.delete(reason="Default log channel was overridden.")
            await value.send(f"{bot.info} The default log channel has been deleted, as it is no longer required.")        

async def system__adminrole(bot, channel, value):
    """The admin role
    The role used to denote which members can configure Solaris. Alongside server administrators, only members with this role can use any of Solaris' configuration commands. Upon selecting a new channel, ChatNoteBot will delete the one that was created during the first time setup should it still exist."""
    if not isinstance(value, discord.Role):
        await channel.send(f"{bot.cross} The admin role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{bot.cross} The everyone role can not be used as the admin role.")
    elif value.name == "@here":
        await channel.send(f"{bot.cross} The here role can not be used as the admin role.")
    elif value.position > channel.guild.me.top_role.position:
        await channel.send(
            f"{bot.cross} The given role can not be used as the admin role as it is above Solaris' top role in the role hierarchy."
        )
    else:
        await bot.db.execute("UPDATE guild_config SET admin_role_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(f"{bot.tick} The admin role has been set to {value.mention}.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The admin role has been set to {value.mention}.")

        if (
            channel.guild.me.guild_permissions.manage_roles
            and (dar := await retrieve.system__defaultadminrole(bot, channel.guild)) is not None
        ):
            await dar.delete(reason="Default admin role was overridden.")
            lc = await retrieve.log_channel(bot, channel.guild)
            await lc.send(f"{bot.info} The default admin role has been deleted, as it is no longer required.")            

async def _gateway__active(bot, channel, value):
    await bot.db.execute("UPDATE gateway SET active = ? WHERE guildId = ?", value, channel.guild.id)            

async def gateway__ruleschannel(bot, channel, value):
    """The rules channel
    The channel that the gate message will be sent to when the module is activated. This channel should contain the server rules, and should be the first channel new members see when they enter the server."""
    if await retrieve._gateway__active(bot, channel.guild):
        await channel.send(f"{bot.cross} This can not be done as the gateway module is currently active.")
    elif not isinstance(value, discord.TextChannel):
        await channel.send(f"{bot.cross} The rules channel must be a Discord text channel in this server.")
    elif not (
        value.permissions_for(channel.guild.me).send_messages
        and value.permissions_for(channel.guild.me).manage_messages
    ):
        await channel.send(
            f"{bot.cross} The given channel can not be used as the rules channel as ChatNoteBot can not send messages to it or manage exising messages there."
        )
    else:
        await bot.db.execute("UPDATE gateway SET rules_channel_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(
            f"{bot.tick} The rules channel has been set to {value.mention}. Make sure this is the first channel new members see when they join."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The rules channel has been set to {value.mention}.")  

async def _gateway__gatemessage(bot, channel, value):
    if value is not None:
        await bot.db.execute("UPDATE gateway SET gate_message_id = ? WHERE guildId = ?", value.id, channel.guild.id)
    else:
        await bot.db.execute("UPDATE gateway SET gate_message_id = NULL WHERE guildId = ?", channel.guild.id)          

async def gateway__blockingrole(bot, channel, value):
    """The blocking role
    The role that ChatNoteBot will give new members upon entering the server, and remove when they accept the server rules. This role should prohibit access to all but the rules channel, or all but a read-only category."""
    if await retrieve._gateway__active(bot, channel.guild):
        await channel.send(f"{bot.cross} This can not be done as the gateway module is currently active.")
    elif not isinstance(value, discord.Role):
        await channel.send(f"{bot.cross} The blocking role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{bot.cross} The everyone role can not be used as the blocking role.")
    elif value.name == "@here":
        await channel.send(f"{bot.cross} The here role can not be used as the blocking role.")
    elif value.position >= channel.guild.me.top_role.position:
        await channel.send(
            f"{bot.cross} The given role can not be used as the blocking role as it is above Solaris' top role in the role hierarchy."
        )
    else:
        await bot.db.execute("UPDATE gateway SET blocking_role_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(
            f"{bot.tick} The blocking role has been set to {value.mention}. Make sure the permissions are set correctly."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The blocking role has been set to {value.mention}.")        

async def gateway__memberroles(bot, channel, values):
    """The member roles
    The role(s) that ChatNoteBot will give members upon accepting the server rules. This is optional, but could be useful if you want members to have specific roles when they join, for example for a levelling system, or to automatically opt them in to server announcements. You can set up to 3 member roles. The roles can be unset at any time by passing no arguments to the command below."""
    values = [values] if not isinstance(values, list) else values

    if (br := await retrieve.gateway__blockingrole(bot, channel.guild)) is None:
        await channel.send(f"{bot.cross} You need to set the blocking role before you can set the member roles.")
    elif values[0] is None:
        await bot.db.execute("UPDATE gateway SET member_role_ids = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The member roles have been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The member roles have been reset.")
    elif len(values) > MAX_MEMBER_ROLES:
        await channel.send(f"{bot.cross} You can only set up to {MAX_MEMBER_ROLES} member roles.")
    elif not all(isinstance(v, discord.Role) for v in values):
        await channel.send(f"{bot.cross} All member roles must be Discord roles in this server.")
    elif any(v.name == "@everyone" for v in values):
        await channel.send(f"{bot.cross} The everyone role can not be used as a member role.")
    elif any(v.name == "@here" for v in values):
        await channel.send(f"{bot.cross} The here role can not be used as a member role.")
    elif any(v == br for v in values):
        await channel.send(f"{bot.cross} No member roles can be the same as the blocking role.")
    elif any(v.position > channel.guild.me.top_role.position for v in values):
        await channel.send(
            f"{bot.cross} One or more given roles can not be used as member roles as they are above ChatNoteBot top role in the role hierarchy."
        )
    else:
        await bot.db.execute(
            "UPDATE gateway SET member_role_ids = ? WHERE guildId = ?",
            common.CSV_SEPARATOR.join(f"{v.id}" for v in values),
            channel.guild.id,
        )
        await channel.send(
            f"{bot.tick} The member roles have been set to {string.list_of([v.mention for v in values])}. Make sure the permissions are set correctly."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The member roles have been set to {string.list_of([v.mention for v in values])}.")        

async def gateway__exceptionroles(bot, channel, values):
    """The exception roles
    The role(s) that, when given to a new member before they accept the server rules, will grant them access to the server. This is optional, but could be useful if you want members to have access upon receiving a premium role, for example, one given by the Patreon bot. You can set up to 3 exception roles. The roles can be unset at any time by passing no arguments to the command below."""
    values = [values] if not isinstance(values, list) else values

    if (br := await retrieve.gateway__blockingrole(bot, channel.guild)) is None:
        await channel.send(f"{bot.cross} You need to set the blocking role before you can set the exception roles.")
    elif values[0] is None:
        await bot.db.execute("UPDATE gateway SET exception_role_ids = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The exception roles have been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The exception roles have been reset.")
    elif len(values) > MAX_EXCEPTION_ROLES:
        await channel.send(f"{bot.cross} You can only set up to {MAX_EXCEPTION_ROLES} exception roles.")
    elif not all(isinstance(v, discord.Role) for v in values):
        await channel.send(f"{bot.cross} All exception roles must be Discord roles in this server.")
    elif any(v.name == "@everyone" for v in values):
        await channel.send(f"{bot.cross} The everyone role can not be used as an exception role.")
    elif any(v.name == "@here" for v in values):
        await channel.send(f"{bot.cross} The here role can not be used as an exception role.")
    elif any(v == br for v in values):
        await channel.send(f"{bot.cross} No exception roles can be the same as the blocking role.")
    else:
        await bot.db.execute(
            "UPDATE gateway SET exception_role_ids = ? WHERE guildId = ?",
            ",".join(f"{v.id}" for v in values),
            channel.guild.id,
        )
        await channel.send(
            f"{bot.tick} The exception roles have been set to {string.list_of([v.mention for v in values])}."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(
            f"{bot.info} The exception roles have been set to {string.list_of([v.mention for v in values])}."
        )        

async def gateway__welcomechannel(bot, channel, value):
    """The welcome channel
    The channel that ChatNoteBot will send welcome messages to upon a member accepting the server rules. If no channel is set, ChatNoteBot will not send welcome messages. The channel can be unset at any time by passing no arguments to the command below. Note that ChatNoteBot does not send welcome messages in all situations, such as if the member received an exception role."""
    if (rc := await retrieve.gateway__ruleschannel(bot, channel.guild)) is None:
        await channel.send(f"{bot.cross} You need to set the rules channel before you can set the welcome channel.")
    elif value is None:
        await bot.db.execute("UPDATE gateway SET welcome_channel_id = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(
            f"{bot.tick} The welcome channel has been reset. ChatNoteBot will stop sending welcome messages."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome channel has been reset.")
    elif not isinstance(value, discord.TextChannel):
        await channel.send(f"{bot.cross} The welcome channel must be a Discord text channel in this server.")
    elif value == rc:
        await channel.send(f"{bot.cross} The welcome channel can not be the same as the rules channel.")
    elif not value.permissions_for(channel.guild.me).send_messages:
        await channel.send(
            f"{bot.cross} The given channel can not be used as the welcome channel as ChatNoteBot can not send messages to it."
        )
    else:
        await bot.db.execute("UPDATE gateway SET welcome_channel_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(f"{bot.tick} The welcome channel has been set to {value.mention}.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome channel has been set to {value.mention}.")        

async def gateway__goodbyechannel(bot, channel, value):
    """The goodbye channel
    The channel that ChatNoteBot will send goodbye messages to upon a member leaving the server. If no channel is set, ChatNoteBot will not send goodbye messages. The channel can be unset at any time by passing no arguments to the command below. Note that ChatNoteBot will only send goodbye messages for members who have accepted the server rules, or members who were in the server before the module was activated."""
    if (rc := await retrieve.gateway__ruleschannel(bot, channel.guild)) is None:
        await channel.send(f"{bot.cross} You need to set the rules channel before you can set the goodbye channel.")
    elif value is None:
        await bot.db.execute("UPDATE gateway SET goodbye_channel_id = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(
            f"{bot.tick} The goodbye channel has been reset. ChatNoteBot will stop sending goodbye messages."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye channel has been reset.")
    elif not isinstance(value, discord.TextChannel):
        await channel.send(f"{bot.cross} The goodbye channel must be a Discord text channel in this server.")
    elif value == rc:
        await channel.send(f"{bot.cross} The goodbye channel can not be the same as the rules channel.")
    elif not value.permissions_for(channel.guild.me).send_messages:
        await channel.send(
            f"{bot.cross} The given channel can not be used as the goodbye channel as ChatNoteBot can not send messages to it."
        )
    else:
        await bot.db.execute("UPDATE gateway SET goodbye_channel_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(f"{bot.tick} The goodbye channel has been set to {value.mention}.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye channel has been set to {value.mention}.")        

async def gateway__timeout(bot, channel, value):
    """The gateway timeout
    The amount of time ChatNoteBot gives new members to react to the gate message before being kicked. This is set in minutes, and can be set to any value between 1 and 60 inclusive. If no timeout is set, the default is 5 minutes. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET timeout = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The timeout has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The timeout has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{bot.cross} The timeout must be an integer number.")
    elif not MIN_TIMEOUT <= value <= MAX_TIMEOUT:
        await channel.send(
            f"{bot.cross} The timeout must be between {MIN_TIMEOUT} and {MAX_TIMEOUT} minutes inclusive."
        )
    else:
        await bot.db.execute("UPDATE gateway SET timeout = ? WHERE guildId = ?", value * 60, channel.guild.id)
        await channel.send(
            f"{bot.tick} The timeout has been set to {value} minute(s). This will only apply to members who enter the server from now."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The timeout has been set to {value} minute(s).")        

async def gateway__gatetext(bot, channel, value):
    """The gate message text
    The message displayed in the gate message. The message can be up to 250 characters in length, and should **not** contain the server rules. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET gate_text = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(
            f"{bot.tick} The gate message text has been reset. The module needs to be restarted for these changes to take effect."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The gate message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{bot.cross} The gate message text must be a string.")
    elif len(value) > MAX_GATETEXT_LEN:
        await channel.send(
            f"{bot.cross} The gate message text must be no longer than {MAX_GATETEXT_LEN:,} characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await bot.db.execute("UPDATE gateway SET gate_text = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(
            f"{bot.tick} The gate message text has been set. The module needs to be restarted for these changes to take effect."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The gate message text has been set to the following: {value}")        

async def gateway__welcometext(bot, channel, value):
    """The welcome message text
    The message sent to the welcome channel (if set) when a new member accepts the server rules. This message can be up to 1,000 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET welcome_text = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The welcome message text has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{bot.cross} The welcome message text must be a string.")
    elif len(value) > MAX_WGTEXT_LEN:
        await channel.send(
            f"{bot.cross} The welcome message text must be no longer than {MAX_WGTEXT_LEN:,} characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await bot.db.execute("UPDATE gateway SET welcome_text = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(f"{bot.tick} The welcome message text has been set.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome message text has been set to the following: {value}")        

async def gateway__goodbyetext(bot, channel, value):
    """The goodbye message text
    The message sent to the goodbye channel (if set) when a member leaves the server. This message can be up to 1,000 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET goodbye_text = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The goodbye message text has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{bot.cross} The goodbye message text must be a string.")
    elif len(value) > MAX_WGTEXT_LEN:
        await channel.send(
            f"{bot.cross} The goodbye message text must be no longer than {MAX_WGTEXT_LEN:,} characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await bot.db.execute("UPDATE gateway SET goodbye_text = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(f"{bot.tick} The goodbye message text has been set.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye message text has been set to the following: {value}")        

async def gateway__welcomebottext(bot, channel, value):
    """The welcome message text for bots
    The message sent to the welcome channel (if set) when a bot joins the server. This message can be up to 500 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET welcome_bot_text = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The welcome bot message text has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome bot message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{bot.cross} The welcome bot message text must be a string.")
    elif len(value) > MAX_WGBOTTEXT_LEN:
        await channel.send(
            f"{bot.cross} The welcome bot message text must be no longer than {MAX_WGBOTTEXT_LEN:,} characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await bot.db.execute("UPDATE gateway SET welcome_bot_text = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(f"{bot.tick} The welcome bot message text has been set.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The welcome bot message text has been set to the following: {value}")    

async def gateway__goodbyebottext(bot, channel, value):
    """The goodbye message text for bots
    The message sent to the goodbye channel (if set) when a bot leaves the server. This message can be up to 500 characters in length. If no message is set, a default will be used instead. The message can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE gateway SET goodbye_bot_text = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The goodbye bot message text has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye bot message text has been reset.")
    elif not isinstance(value, str):
        await channel.send(f"{bot.cross} The goodbye bot message text must be a string.")
    elif len(value) > MAX_WGBOTTEXT_LEN:
        await channel.send(
            f"{bot.cross} The goodbye bot message text must be no longer than {MAX_WGBOTTEXT_LEN:,} characters in length."
        )
    elif not string.text_is_formattible(value):
        await channel.send(f"{bot.cross} The given message is not formattible (probably unclosed brace).")
    else:
        await bot.db.execute("UPDATE gateway SET goodbye_bot_text = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(f"{bot.tick} The goodbye bot message text has been set.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The goodbye bot message text has been set to the following: {value}")            

async def warn__warnrole(bot, channel, value):
    """The warn role
    The role that members need to have in order to warn other members, typically a moderator or staff role. If this is not set, only server administrators will be able to warn members. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE warn SET warn_role_id = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The warn role has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The warn role has been reset.")
    elif not isinstance(value, discord.Role):
        await channel.send(f"{bot.cross} The warn role must be a Discord role in this server.")
    elif value.name == "@everyone":
        await channel.send(f"{bot.cross} The everyone role can not be used as the warn role.")
    elif value.name == "@here":
        await channel.send(f"{bot.cross} The here role can not be used as the warn role.")
    else:
        await bot.db.execute("UPDATE warn SET warn_role_id = ? WHERE guildId = ?", value.id, channel.guild.id)
        await channel.send(f"{bot.tick} The warn role has been set to {value.mention}.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The warn role has been set to {value.mention}.")        

async def warn__maxpoints(bot, channel, value):
    """The max points total
    The number of points a member needs in total to get banned from a warning. This can be set to any value between 5 and 99 inclusive. If no value is set, the default is 12. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE warn SET max_points = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The max points total has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The max points total has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{bot.cross} The max points total must be an integer number.")
    elif not MIN_POINTS <= value <= MAX_POINTS:
        await channel.send(
            f"{bot.cross} The max points total must be between {MIN_POINTS} and {MAX_POINTS} inclusive."
        )
    else:
        await bot.db.execute("UPDATE warn SET max_points = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(
            f"{bot.tick} The max points total has been set to {value}. Members currently at or exceeding this total will not be retroactively banned."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The max points total has been set to {value}.")        

async def warn__maxstrikes(bot, channel, value):
    """The max strikes per offence
    The number of times a member needs to be warned of a particular offence to get banned from a warning. This is per offence, and not a total number of strikes. This can be set to any value between 1 and 9 inclusive. If no value is set, the default is 3. This can be reset at any time by passing no arguments to the command below."""
    if value is None:
        await bot.db.execute("UPDATE warn SET max_strikes = NULL WHERE guildId = ?", channel.guild.id)
        await channel.send(f"{bot.tick} The max strikes per offence has been reset.")
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The max strikes per offence has been reset.")
    elif not isinstance(value, int):
        await channel.send(f"{bot.cross} The max strikes per offence must be an integer number.")
    elif not MIN_STRIKES <= value <= MAX_STRIKES:
        await channel.send(
            f"{bot.cross} The max strikes per offence must be between {MIN_STRIKES} and {MAX_STRIKES} inclusive."
        )
    else:
        await bot.db.execute("UPDATE warn SET max_strikes = ? WHERE guildId = ?", value, channel.guild.id)
        await channel.send(
            f"{bot.tick} The max strikes per offence has been set to {value}. Members currently at or exceeding this total will not be retroactively banned."
        )
        lc = await retrieve.log_channel(bot, channel.guild)
        await lc.send(f"{bot.info} The max strikes per offence has been set to {value}.")        