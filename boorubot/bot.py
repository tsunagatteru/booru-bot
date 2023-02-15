from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import ImageInfo
from mautrix.errors import request
from .image import get_image
from .db import store_tags, get_tags, change_tags_listing, get_tags_listing
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
import mimetypes
from typing import Type
import pymongo


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("ip")
        helper.copy("port")
        helper.copy("user")
        helper.copy("pass")
        helper.copy("db")


class BooruBot(Plugin):
    async def start(self) -> None:
        self.config.load_and_update()

    @command.new(name="tags", aliases=["t"])
    async def respond2(self, evt: MessageEvent) -> None:
        client = pymongo.MongoClient("mongodb://" + str(self.config["user"]) + ":" + str(self.config["pass"]) + "@" +
                                     str(self.config["ip"]) + ":" + str(self.config["port"]))
        target = client[str(self.config["db"])]["tags_listing"]
        await change_tags_listing(evt.sender, target)
        await evt.reply("Tags listing " + await get_tags_listing(evt.sender, target))

    @command.new(name="get", aliases=["g"])
    @command.argument("prompt", pass_raw=True, required=False)
    async def respond(self, evt: MessageEvent, prompt: str) -> None:
        arguments = prompt.split('!')
        tags = arguments[0]
        try:
            times = (arguments[1])
        except IndexError:
            times = "1"
        if times.isdigit():
            times = int(times)
        else:
            times = 1
        client = pymongo.MongoClient("mongodb://" + str(self.config["user"]) + ":" + str(self.config["pass"]) + "@" +
                                     str(self.config["ip"]) + ":" + str(self.config["port"]))
        target = client[str(self.config["db"])]["previous_tags"]
        if tags == "-":
            tags = await get_tags(evt.sender, target)
            if tags == "-":
                await evt.reply("No previous requests")
                return None
        target = client[str(self.config["db"])]["tags_listing"]
        tags_listing = await get_tags_listing(evt.sender, target)
        for i in range(times):
            pic = await get_image(tags)
            if pic.valid:
                mime_type = mimetypes.guess_type(pic.name)[0]
                uri = await self.client.upload_media(pic.image, mime_type=mime_type, filename=pic.name)
                try:
                    await self.client.send_image(evt.room_id, url=uri, file_name=pic.name,
                                                 info=ImageInfo(mimetype=mime_type))
                    if tags_listing == "enabled":
                        await evt.respond(pic.tags)
                except request.MLimitExceeded:
                    await evt.reply("Limit exceeded")
            else:
                await evt.reply("No results")
                return None
        target = client[str(self.config["db"])]["previous_tags"]
        await store_tags(evt.sender, tags, target)

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
