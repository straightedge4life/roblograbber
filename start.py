from libs.grabber import grabber
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
from lxml.html import fromstring, tostring
import os
from db.mysql import mysql


def start():
    url = 'http://www.roblog.top'
    articles_rule = '//div[@id="main"]/article'
    article_url_rule = './h2/a/@href'
    pageinate_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'
    articles_urls = []

    #先把首页挖出来
    paginate = getPage(url , pageinate_rule)
    
    #根据分页信息获取最大页码，遍历拼接每一页的链接
    pages = [ {'url':url+'/page/'+str(i) , 'rule':articles_rule} for i in range(1, int(paginate[0])+1)]
    
    #开线程抓取每页的内容，抓取每页的文章链接
    articles_futures = threadCreate(10 , getPage , *pages)
    for items in articles_futures :
        for item in items.result() :
            url = locateHTML(item , article_url_rule)[0]
            articles_urls.append({'url':url})
    
    #再开线程抓取每篇文章的内容
    threadCreate(10 , getArticlesPage , *articles_urls)

#专门用来抓取单个文章页
def getArticlesPage(url):
    title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'
    content_rule = '//*[@id="main"]'
    g = grabber()
    pageHTML = getHTML(g.sendRquest(url).text)
    title = locateHTML(pageHTML , title_rule)
    content = locateHTML(pageHTML , content_rule)
    #三目判断一下
    title = title[0] if title else ''  
    content =  tostring(content[0]) if content else ''
    #入库
    storeToDb(title , content , url)

#保存到数据库
def storeToDb(title , content , url) :
    client = mysql().client

    #去重
    duplicateCheckSql = """SELECT `id` , `url` FROM `articles` WHERE `url` ='%(url)s'  """ % dict(url = url)
    client.query(duplicateCheckSql)
    res = client.store_result()
    if not res.fetch_row(how = 1) :
        c = client.cursor()
        c.execute("""INSERT INTO `articles` (`title`,`content`,`url`) VALUES(%s,%s,%s);""",(title , content , url))
        client.commit()

#发起请求 返回html对象
def getPage(url , rule):
    g = grabber()
    html = getHTML(g.sendRquest(url).text)
    targetHtml = locateHTML(html , rule)
    return targetHtml

#解析html
def getHTML(response):
    return etree.HTML(response)

#使用xpath定位
def locateHTML(html , rule):
    return html.xpath(rule)
    
#开线程处理
def threadCreate(max_workers , fn , *args):
    futures = []
    with ThreadPoolExecutor(max_workers) as pool:
         for item in args :
            future = pool.submit(fn , **item)
            futures.append(future)
    return futures

start()