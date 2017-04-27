import discord

import utils


class MessageDetector(utils.Detector):
    async def check(self, m: discord.Message):
        return await self.parse_content(m, m.content)


def setup(bot):
    bot.add_detector(MessageDetector(bot))
