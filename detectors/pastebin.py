import re

import discord

import utils


class PastebinDetector(utils.Detector):
    patt = re.compile(r"https?:\/\/pastebin\.com\/"
                      r"([a-zA-Z0-9]+)")
    async def check(self, m: discord.Message):
        match = self.patt.search(m.content)

        if match is not None:
            # contains pastebin link, download contents
            # TODO: handle multiple hastebin links
            raw_link = "https://pastebin.com/raw/{}".format(match.group(1))
            paste_contents = await utils.get_url(raw_link)

            # Check content
            match, token = await utils.check_token(self.bot, paste_contents)

            if match is False:
                # No valid token
                return

            # Process reporting
            await self.bot.process_token(m, match, token)

            # If a token is found, return True
            return True


def setup(bot):
    bot.add_detector(PastebinDetector(bot))
