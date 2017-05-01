import re

import discord

import utils


class GithubDetector(utils.Detector):
    patt = re.compile(r"https?:\/\/github.com\/([a-zA-Z0-9_\-]+)\/"
                      r"([a-zA-Z0-9_\-]+)(\/tree\/[a-zA-Z0-9_\-]+)?")

    extensions = (
        # Langs to check
        "py", "js", "lua", "java", "c",
        "txt", "cpp", "cs", "rb", "hs",
    )

    configs = (
        # Config formats
        "ini", "cfg", "yaml", "json",
    )

    check_names = (
        "config", "bot", "run",
    )

    base_url = "https://api.github.com/repos/{}/{}/git/trees/{}?recursive=1"
    file_url = "https://raw.githubusercontent.com/{}/{}/{}/{}"

    def get_files(self, data: dict):
        files = []
        for file in data["tree"]:
            # Only check files, not directories
            if file["type"] == "tree":
                continue

            # Get the file and extension
            file = file["path"]
            ext = file.rpartition(".")[-1]

            if ext in self.extensions:
                # Check if it has a filename we're looking for
                filename = file.rpartition("/")[-1]
                if any(name in filename for name in self.check_names):
                    # Mark this file to be checked
                    files.append(file)

            elif ext in self.configs:
                # Mark this file to be checked
                files.append(file)
        return files

    async def check(self, m: discord.Message):
        # Try to find a github link
        match = self.patt.search(m.content)
        if not match:
            return

        # Get data
        owner = match.group(1)
        repo = match.group(2)
        tree = match.group(3) or "master"

        tree = tree.lstrip("/tree/")

        # Get repo structure
        api_url = self.base_url.format(owner, repo, tree)
        data = await utils.get_url(api_url, method="json")

        # Get files to check
        files = self.get_files(data)
        if not files:
            # No files to check
            return

        for file in files:
            # Get file contents
            url = self.file_url.format(owner, repo, tree, file)
            content = await utils.get_url(url)

            p = await self.parse_content(m, content)
            if p:
                return True


def setup(bot):
    bot.add_detector(GithubDetector(bot))
