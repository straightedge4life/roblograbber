import aiohttp
import asyncio


class AsyncGrabber:
    # UA 默认用火狐
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }

    # 代理
    proxies = {}

    methods = ['GET', 'POST']

    def __init__(self, headers=None, proxies=None):
        if type(headers) is dict:
            self.headers = headers
        if type(proxies) is dict:
            self.proxies = proxies

