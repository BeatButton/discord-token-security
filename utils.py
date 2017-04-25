import re
import hashlib

import discord
import aiohttp

# Token RegEx
patt = re.compile(r"([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]"
                  r"{27}|mfa\.[a-zA-Z0-9_\-]{84})")

# Use a single session
session = aiohttp.ClientSession()


class Detector:
    def __init__(self, bot):
        self.bot = bot

    async def check(self, m: discord.Message):
        # This function is called to check if a token exists
        # If a token is found, make sure to return True
        # To report to the user, call `self.bot.process_token`
        pass


async def get_url(url: str, headers: dict=None, method: str="text"):
    # Shorthand function to get data from an URL
    async with session.get(url, headers=headers or {}) as resp:
        if 200 <= resp.status < 300:
            data = await getattr(resp, method)()
            return data
        else:
            return None


def check_length(content: str):
    # Ckeck if there exists a token-like
    # string is in a given `content`
    return patt.search(content)


async def check_valid(tok: str):
    # See if this is a valid token
    data = await get_url("https://discordapp.com/api/users/@me",
                         {"Authorization": tok}, "json")

    if data is not None:
        # Data was found, valid token
        return data

    # Retry with `Bot ` prefixed if not a 2FA token
    if not tok.startswith("mfa."):
        data = await get_url("https://discordapp.com/api/users/@me",
                             {"Authorization": "Bot " + tok}, "json")
    return data or False


async def check_token(bot, content: str):
    # Assert RegEx pattern
    match = check_length(content)

    if match is None:
        return False, None

    token = match.group(0)

    # Check if it's logged already
    hashed = hashlib.sha256(token).hexdigest()
    if hashed in bot.cache:
        # We already checked it,
        # no need to make API calls again,
        # nor do we have to message the user again
        return False, None

    # Check if the token is valid
    valid = await check_valid(token)
    x = valid or False
    return x, token


async def get_user(token: str):
    # Get the owner of a bot token
    data = await get_url("https://discordapp.com/api/oauth2/applications/@me",
                         {"Authorization": "Bot " + token}, "json")
    return data["owner"]
