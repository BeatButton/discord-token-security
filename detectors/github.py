import re

import discord

import utils

patt = re.compile(r"https?:\/\/github.com\/([a-zA-Z0-9_\-]+)\/"
                  r"([a-zA-Z0-9_\-]+)(\/tree\/[a-zA-Z0-9_\-]+)?")

extensions = [
    # Langs to check
    "py", "js", "lua", "java", "c",
    "txt", "cpp", "cs", "rb", "hs",
]

configs = [
    # Config formats
    "ini", "cfg", "yaml", "json",
]

check_names = [
    "config", "bot", "run",
]

base_url = "https://api.github.com/repos/{}/{}/git/trees/{}?recursive=1"
file_url = "https://raw.githubusercontent.com/{}/{}/{}/{}"


class GithubDetector(utils.Detector):
    def get_files(self, data: dict):
        files = []
        for file in data["tree"]:
            # Only check files, not directories
            if file["type"] == "tree":
                continue

            # Get the file and extension
            file = file['path']
            ext = file.split(".")[-1]

            if ext in extensions:
                # Check if it has a filename we're looking for
                if any(name in file.split("/")[-1] for name in check_names):
                    # Mark this file to be checked
                    files.append(file)

            elif ext in configs:
                # Mark this file to be checked
                files.append(file)
        return files

    async def check(self, m: discord.Message):
        # Try to find a github link
        match = patt.search(m.content)
        if not match:
            return

        # Get data
        owner = match.group(1)
        repo = match.group(2)
        tree = match.group(3) or "master"

        # /tree/BRANCH -> BRANCH
        if tree.startswith("/"):
            tree = tree[6:]

        # Get repo structure
        api_url = base_url.format(owner, repo, tree)
        data = await utils.get_url(api_url, method="json")

        # Get files to check
        files = self.get_files(data)
        if not files:
            # No files to check
            return

        for f in files:
            # Get file contents
            url = file_url.format(owner, repo, tree, f)
            content = await utils.get_url(url)

            p = await self.parse_content(m, content)
            if p:
                return True


def setup(bot):
    bot.add_detector(GithubDetector(bot))
