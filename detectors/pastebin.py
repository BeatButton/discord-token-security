import re

import discord

import utils

patt = re.compile(r"https?:\/\/pastebin\.com\/"
                  r"([a-zA-Z0-9]+)")


class PastebinDetector(utils.Detector):
    async def check(self, m: discord.Message):
        match = patt.search(m.content)

        if match is not None:
            # contains pastebin link, download contents
            # TODO: handle multiple hastebin links
            raw_link = "https://pastebin.com/raw/{}".format(match.group(1))
            paste_contents = await utils.get_url(raw_link)

            p = await self.parse_content(m, paste_contents)
            if p:
                return True


def setup(bot):
    bot.add_detector(PastebinDetector(bot))
