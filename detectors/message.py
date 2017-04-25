import discord

import utils


class MessageDetector(utils.Detector):
    async def check(self, m: discord.Message):
        # Check content
        match, token = await utils.check_token(self.bot, m.content)

        if match is False:
            # No valid token
            return

        # Process reporting
        await self.bot.process_token(m, match, token)

        # If a token is found, return True
        return True


def setup(bot):
    bot.add_detector(MessageDetector(bot))
