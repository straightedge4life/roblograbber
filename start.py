from libs.grabber import grabber
from libs.locater import locater
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
from lxml.html import fromstring, tostring
import os
from db.mysql import mysql
import chardet


def start():
    url = 'http://www.roblog.top'
    #一些xpath规则
    articles_rule = '//div[@id="main"]/article'
    article_url_rule = './h2/a/@href'
    pageinate_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'
    title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'

    #先把首页挖出来
    paginate = getPage(url , pageinate_rule)
    pages = range(1, int(paginate[0])+1)

    #开个list保存每个进程的future对象
    articles_futures = []
    with ThreadPoolExecutor(max_workers = 10) as index_processer:
        for i in pages :
            p = index_processer.submit(getPage , url = url+'/page/'+str(i) , rule = articles_rule)
            articles_futures.append(p)

    #在全部进程完成后再从list通过.result()抽取函数所返回的数据
    articles_urls = []
    for article_future in articles_futures :
        for article in article_future.result() :
            articles_urls.append(article.xpath(article_url_rule)[0])
           
        
    with ThreadPoolExecutor(max_workers = 10) as article_processer:
        detail_futures = []
        for url in articles_urls:
            #抓文章标题
            future = article_processer.submit(getArticlesPage , url = url )
            detail_futures.append(future)

        insertData = []
        for detail in detail_futures :
            insertData.append(detail.result())
            


    #写入到文件
    # file_path = r'%s/%s.txt' % (os.path.dirname(os.path.abspath(__file__)), 'title')        
    # for title_future in title_futures :
    #     with  open(file_path , 'a+' , encoding = 'utf-8') as f :
            
    #         f.write(str(title_future.result()[0])+'\n')

    client = mysql().client
    c = client.cursor()
    c.executemany("""INSERT INTO `articles` (`title`,`content`,`url`) VALUES(%s,%s,%s);""",insertData)
    client.commit()
       
    
    
            
        
    

def getArticlesPage(url):
    # 格式
    # [('title' , 'url' , 'content'),('title' , 'url' , 'content'),('title' , 'url' , 'content')]
    #
    data = []
    title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'
    content_rule = '//*[@id="main"]'
    g = grabber()
    page = etree.HTML(g.sendRquest(url).text)
    
    title = page.xpath(title_rule)

    if title == () :
        title = ''
    else:
        title = title[0]

    content = page.xpath(content_rule)

    if content == () :
        content = ''
    else:
        content = tostring(content[0])

    data.append(title)
    data.append(content)
    data.append(url)
    return tuple(data)

def getPage(url , rule):
    g = grabber()
    return etree.HTML(g.sendRquest(url).text).xpath(rule)
    
start()




