import aiohttp
from xml.etree import ElementTree
import random
import math


async def make_request(session, url):
    async with session.get(url) as response:
        return await response.read()


class Result:
    def __init__(self, image, name, valid):
        self.image = image
        self.name = name
        self.valid = valid


async def get_image(tags):
    async with aiohttp.ClientSession() as session:
        url = ("https://safebooru.org/index.php?page=dapi&s=post&q=index&tags="+tags)
        post_front = await make_request(session, url + "&limit=0")
        out = Result("", "", True)
        tree = ElementTree.fromstring(post_front)
        post_count = int(tree.get('count'))
        if post_count == 0:
            out.valid = False
            return out
        post_number = random.randrange(post_count)
        page_number = math.floor(post_number/100)
        url += "&pid=" + str(page_number)
        url += "."
        if post_number < 10:
            url += "0"
        url += str(post_number % 100)
        page_front = await make_request(session, url)
        tree = ElementTree.fromstring(page_front)
        image_url = tree.find('post').get('file_url')
        image_tags = tree.find('post').get('tags')
        out.image = await make_request(session, image_url)
        out.name = image_url.replace('https://', '')
        out.tags = image_tags
        return out
