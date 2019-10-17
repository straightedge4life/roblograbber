import aiohttp


class AsyncGrabber:
    # UA 默认用火狐
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }

    # 代理
    proxies = {}

    # 请求方法
    methods = ['GET', 'POST']

    cookie = {}

    def __init__(self, headers=None, proxies=None, cookie=None):
        if type(headers) is dict:
            self.headers = headers

        if type(proxies) is dict:
            self.proxies = proxies

        if type(cookie) is dict:
            self.cookie = cookie

    async def send_request(self, url: str, method: str = "GET"):
        """
        异步发送请求
        :param url:
        :param method:
        :return:
        """
        if method not in self.methods:
            raise RuntimeError("Request method doesn't exists.")

        result = None

        try:
            async with aiohttp.ClientSession(cookies=self.cookie, headers=self.headers) as session:
                async with session.request(method=method, url=url) as resp:
                    result = await resp.text()
        except Exception as e:
            raise ()

        return result, url

