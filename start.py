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

    # 先把首页挖出来
    paginate = get_page(url, paginate_rule)[0]

    # 根据分页信息获取最大页码，遍历拼接每一页的链接
    page_num = range(1, int(paginate) + 1)

    # 构建参数，因为ThreadPoolExecutor.map()方法里面会通过zip()将参数遍历
    # 然后再调用自身的ThreadPoolExecutor.submit()
    # 所以结构会是[[参数1, 参数1, 参数1], [参数2, 参数2, 参数2]]
    pages_args = [[url+'/page/'+str(i) for i in page_num], [articles_rule for i in page_num]]

    with ThreadPoolExecutor(10) as pool:
        for pre_page in pool.map(get_page, *pages_args):
            for page_detail_result in pool.map(get_articles_page, [locate_html(item, article_url_rule)[0] for item in pre_page]):
                print(page_detail_result)
                print('-------------------------')


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
    return 'Article ['+title+'] has been store success!'


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


def get_page(url: str, rule: str):
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


if __name__ == '__main__':
    start()
