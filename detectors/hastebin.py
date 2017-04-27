import re

import discord

import utils

# Hastebin URL RegEx
patt = re.compile(r"https?:\/\/(hastebin\.com"
                  r"|paste\.safe\.moe)/([a-z]{10})")


class HastebinDetector(utils.Detector):
    async def check(self, m: discord.Message):
        match = patt.search(m.content)

        # ex:
        # match.groups() -> (hastebin, uxorezaqib)

        if match is not None:
            # contains hastebin link
            # TODO: handle multiple hastebin links
            raw_link = "https://{}/raw/{}".format(*match.groups())
            bin_contents = await utils.get_url(raw_link)

            p = await self.parse_content(m, bin_contents)
            if p:
                return True


def setup(bot):
    bot.add_detector(HastebinDetector(bot))
