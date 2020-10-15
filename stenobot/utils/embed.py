# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/embed.py

import common
from datetime import datetime
from discord import Embed
from stenobot.utils import DEFAULT_EMBED_COLOUR


class EmbedConstructor:
    def __init__(self, bot):
        self.bot = bot

    def build(self, **kwargs):
        ctx = kwargs.get("ctx")

        embed = Embed(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            colour=(
                kwargs.get("colour")
                or (ctx.author.colour if ctx and ctx.author.colour.value else None)
                or DEFAULT_EMBED_COLOUR
            ),
            timestamp=datetime.utcnow(),
        )

        embed.set_author(name=kwargs.get("header", f"{common.BOT_NAME}"))
        embed.set_footer(
            text=kwargs.get("footer", f"Invoked by {ctx.author.display_name}" if ctx else r"\o/"),
            icon_url=ctx.author.avatar_url if ctx else self.bot.user.avatar_url,
        )

        # FIXME: In d.py 1.4, `Embed.Empty` will be supported.
        if thumbnail := kwargs.get("thumbnail"):
            embed.set_thumbnail(url=thumbnail)

        # FIXME: In d.py 1.4, `Embed.Empty` will be supported.
        if image := kwargs.get("image"):
            embed.set_image(url=image)

        for name, value, inline in kwargs.get("fields", ()):
            embed.add_field(name=name, value=value, inline=inline)

        return embed