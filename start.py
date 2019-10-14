from libs.grabber import Grabber
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
from lxml.html import fromstring, tostring
from db.mysql import mysql


def start():
    """
    开始执行
    :return:
    """
    url = 'http://www.roblog.top'
    articles_rule = '//div[@id="main"]/article'
    article_url_rule = './h2/a/@href'
    paginate_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'
    articles_urls = []

    # 先把首页挖出来
    paginate = get_page(url, paginate_rule)

    # 根据分页信息获取最大页码，遍历拼接每一页的链接
    pages = [{'url': url+'/page/'+str(i), 'rule': articles_rule} for i in range(1, int(paginate[0])+1)]
    
    # 开线程抓取每页的内容，抓取每页的文章链接
    articles_futures = thread_create(10, get_page, *pages)
    for items in articles_futures:
        for item in items.result():
            url = locate_html(item, article_url_rule)[0]
            articles_urls.append({'url': url})
    
    # 再开线程抓取每篇文章的内容
    thread_create(10, get_articles_page, *articles_urls)


def get_articles_page(url):
    """
    专门用来抓取单个文章页
    :param url: 文章页路径
    :return:
    """
    title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'
    content_rule = '//*[@id="main"]'
    g = Grabber()
    page_html = get_html(g.send_request(url).text)
    title = locate_html(page_html, title_rule)
    content = locate_html(page_html, content_rule)
    # 三目判断一下
    title = title[0] if title else ''  
    content = tostring(content[0]) if content else ''
    # 入库
    store_to_db(title, content, url)


def store_to_db(title, content, url):
    """
    保存到数据库
    :param title:
    :param content:
    :param url:
    :return:
    """
    client = mysql().client

    # 去重
    duplicate_check_sql = """SELECT `id` , `url` FROM `articles` WHERE `url` ='%(url)s'  """ % dict(url=url)
    client.query(duplicate_check_sql)
    res = client.store_result()
    if not res.fetch_row(how=1):
        c = client.cursor()
        c.execute("""INSERT INTO `articles` (`title`,`content`,`url`) VALUES(%s,%s,%s);""", (title, content, url))
        client.commit()


def get_page(url, rule):
    """
    发起请求 返回html对象
    :param url:
    :param rule:
    :return:
    """
    g = Grabber()
    html = get_html(g.send_request(url).text)
    target_html = locate_html(html, rule)
    return target_html


def get_html(response):
    """
    解析html
    :param response:
    :return:
    """
    return etree.HTML(response)


def locate_html(html, rule):
    """
    使用xpath定位
    :param html:
    :param rule:
    :return:
    """
    return html.xpath(rule)
    
    
def thread_create(max_workers, fn, *args):
    """
    开线程处理任务
    :param max_workers:
    :param fn:
    :param args:
    :return:
    """
    futures = []
    with ThreadPoolExecutor(max_workers) as pool:
        for item in args :
            future = pool.submit(fn, **item)
            futures.append(future)
    return futures


start()