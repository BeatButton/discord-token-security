import discord

import utils


extensions = (
    # Langs to check
    "py", "js", "lua", "java", "c",
    "txt", "cpp", "cs", "rb", "hs",

    # Config formats
    "ini", "cfg", "yaml", "json",

    # Other files to check?
    ...
)


class AttachmentDetector(utils.Detector):
    async def check(self, m: discord.Message):
        for file in m.attachments:
            ext = file['filename'].split(".")[-1]
            if ext in self.extensions:
                # Extension is one we check, download content
                content = await utils.get_url(file['url'])

                p = await self.parse_content(m, content)
                if p:
                    return True


def setup(bot):
    bot.add_detector(AttachmentDetector(bot))
