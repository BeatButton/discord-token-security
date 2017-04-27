import discord

import utils


class EmbedDetector(utils.Detector):
    async def check(self, m: discord.Message):
        for e in m.embeds:
            # Check content
            for c in ["title", "description"]:
                p = await self.parse_content(m, getattr(e, c))
                if p:
                    return True

            for f in e["fields"]:
                p = await self.parse_content(m, f["value"])
                if p:
                    return True


def setup(bot):
    bot.add_detector(EmbedDetector(bot))
