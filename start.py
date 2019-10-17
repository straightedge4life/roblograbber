from lxml import etree
from lxml.html import tostring
from db.mysql import Mysql
from libs.AsyncGrabber import AsyncGrabber
import asyncio


def async_start():
    """
    开始爬虫
    :return:
    """
    url = 'http://www.roblog.top'
    article_url_rule = '//h2/a/@href'
    max_page_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'
    title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'
    content_rule = '//*[@id="main"]'

    g = AsyncGrabber()
    event_loop = asyncio.get_event_loop()

    # 得出首页最大页码数
    # ps: g.send_request(url)返回response和url，如果只用一个变量接收的话会是一个元组(response, url)
    result, url = event_loop.run_until_complete(g.send_request(url))
    max_page = locate_html(etree.HTML(result), max_page_rule)
    paginate_range = range(1, int(max_page[0]) + 1)

    # 爬取所有列表页的内容
    tasks = [g.send_request(url + '/page/' + str(i)) for i in paginate_range]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))

    detail_tasks = []

    # 从每页的列表页提取出文章url
    for curr_page, url in results:
        curr_detail_tasks = [
            g.send_request(article_url)
            for article_url in locate_html(etree.HTML(curr_page), article_url_rule)
        ]
        detail_tasks += curr_detail_tasks

    detail_results = event_loop.run_until_complete(asyncio.gather(*detail_tasks))

    # 爬取每一篇文章
    for detail_page, detail_url in detail_results:
        detail_html = etree.HTML(detail_page)
        title = locate_html(detail_html, title_rule)
        content = locate_html(detail_html, content_rule)
        # 三目判断一下
        title = title[0] if title else ''
        content = tostring(content[0]) if content else ''
        # 入库
        if store_to_db(title, content, detail_url):
            print('Article [' + title + '] has been store success!')
        else:
            print('Article [' + title + '] has been store fail!')


def store_to_db(title, content, url):
    """
    保存到数据库
    :param title:
    :param content:
    :param url:
    :return:
    """
    client = Mysql().client

    # 去重
    duplicate_check_sql = """SELECT `id` , `url` FROM `articles` WHERE `url` ='%(url)s'  """ % dict(url=url)
    client.query(duplicate_check_sql)
    res = client.store_result()
    if not res.fetch_row(how=1):
        c = client.cursor()
        c.execute("""INSERT INTO `articles` (`title`,`content`,`url`) VALUES(%s,%s,%s);""", (title, content, url))
        client.commit()
        return True
    else:
        return False


def locate_html(html, rule):
    """
    使用xpath定位
    :param html:
    :param rule:
    :return:
    """
    return html.xpath(rule)


if __name__ == '__main__':
    async_start()
