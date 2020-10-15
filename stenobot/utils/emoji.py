# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/__init__.py

from discord import utils

# If {common.BOT_NAME} can't use the correct emojis, fall back to these.
ALTERNATIVES = {
    "confirm": "✅",
    "cancel": "❎",
    "exit": "⏏️",
    "info": "ℹ️",
    "loading": "⏱️",
    "option1": "1️⃣",
    "option2": "2⃣",
    "option3": "3⃣",
    "option4": "4⃣",
    "option5": "5⃣",
    "option6": "6⃣",
    "option7": "7⃣",
    "option8": "8⃣",
    "option9": "9⃣",
    "pageback": "◀️",
    "pagenext": "▶️",
    "stepback": "⏪",
    "stepnext": "⏩",
}


class EmojiGetter:
    def __init__(self, bot):
        self.bot = bot

    def get(self, name):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            emoj = utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name]
            return emoj
        else:
            return ALTERNATIVES[name]

    def get_many(self, *names):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            return [utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name] for name in names]
        else:
            return [ALTERNATIVES[name] for name in names]

    def yield_many(self, *names):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            for name in names:
                yield utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name]
        else:
            yield [ALTERNATIVES[name] for name in names]

    def mention(self, name):
        hub = self.bot.get_cog("Hub")

        if getattr(hub, "guild", None) is not None:
            return f"{utils.get(hub.guild.emojis, name=name) or ALTERNATIVES[name] or ''}"
        else:
            return ALTERNATIVES[name] or ""
