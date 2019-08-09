from libs.grabber import grabber
from libs.locater import locater
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import os

def start():
    url = 'https://www.roblog.top'
    #一些xpath规则
    articles_rule = '//div[@id="main"]/article'
    article_url_rule = './h2/a/@href'
    pageinate_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'
    content_title_rule = '/html/body/div/div/div/div[1]/article/h1/a/text()'

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
        title_futures = []
        for url in articles_urls:
            #抓文章标题
            future = article_processer.submit(getPage , url = url , rule = content_title_rule)
            title_futures.append(future)

    file_path = r'%s/%s.txt' % (os.path.dirname(os.path.abspath(__file__)), 'title')        
    for title_future in title_futures :
        with  open(file_path , 'a+' , encoding = 'utf-8') as f :
            f.write(str(title_future.result()[0])+'\n')
       
    
    
            
        
    

   


def getPage(url , rule):
    g = grabber()
    return etree.HTML(g.sendRquest(url).text).xpath(rule)
    
start()

   