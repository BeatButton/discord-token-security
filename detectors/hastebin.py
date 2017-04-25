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

            # Check content
            match, token = await utils.check_token(self.bot, bin_contents)

            if match is False:
                # No valid token
                return

            # Process reporting
            await self.bot.process_token(m, match, token)

            # If a token is found, return True
            return True


def setup(bot):
    bot.add_detector(HastebinDetector(bot))
