import importlib
import logging
import hashlib

import yaml
import discord

import utils


logging.basicConfig(level=logging.INFO)

# Load config
with open('config.yaml') as f:
    cfg = yaml.load(f)


class Bot(discord.Client):
    cache = {}  # set of hashed tokens
    dets = {}   # dict of Detectors

    def __init__(self, cfg: dict, *args, **kwargs):
        # Save our token as variable
        self.token_ = cfg.get('token')

        # Load all detectors from the config
        for det in cfg['detectors']:
            lib = importlib.import_module(det)
            lib.setup(self)

        # Init client
        super().__init__(*args, **kwargs)

    def run(self, token=None):
        super().run(token or self.token_)

    def add_detector(self, det: utils.Detector):
        self.dets[det.__class__.__name__] = det

    async def process_token(self, m: discord.Message,
                            match: dict, token: str):
        hashed = hashlib.sha256(token).hexdigest()

        # Mark token as checked
        self.cache.add(hashed)

        did_delete = False
        try:
            # Try to delete the message
            await self.delete_message(m)
            did_delete = True
        except:
            pass

        msg = ("Hey, a token for {}#{} (<@{}>) just leaked in <#{}>"
               ", you might want to reset it.")\
            .format(match["username"], match["discriminator"],
                    match["id"], m.channel.id)

        id = match["id"]
        if match.get("bot") is True:
            # It's a bot, send to the owner instead
            user = await utils.get_user(token)
            id = user["id"]

        # Try to find the owner
        t = discord.utils.get(self.get_all_members(), id=id)

        if t is None:
            # Owner not found, mention them in that channel instead
            t = m.channel
            msg = "<@{}>\n".format(id) + msg

        if did_delete:
            msg += ("\nI went ahead and deleted the message for you,"
                    " but you should reset it anyways.")

        try:
            # Send the message.
            # If this fails, we have no permission
            # to message them directly OR we have no permission
            # to send to the channel
            await self.send_message(t, msg)
        except:
            # Resend to the channel
            # This will fail if we do not have permission
            if not msg.startswith("<"):
                msg = "<@{}>\n".format(id) + msg
            await self.send_message(m.channel, msg)

    async def on_message(self, m: discord.Message):
        its = self.dets[:]
        res = None

        # When a token is found, a Detector should return True
        while res is not True:
            try:
                # Get the next Detector
                det = next(its)
            except StopIteration:
                break

            # Check, and stop if a token was found
            res = await det.check(m)


bot = Bot(cfg)
bot.run()
