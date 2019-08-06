from libs.grabber import grabber
from libs.locater import locater
from lxml import etree
from concurrent.futures import ThreadPoolExecutor

def start():
    url = 'https://www.roblog.top'
    #一些xpath规则
    articles_rule = '//div[@id="main"]/article'
    article_url_rule = './h2/a/@href'
    pageinate_rule = '//ol[@class="page-navigator"]/li[last()-1]/a/text()'

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
           
        
    
    
            
        
    

   


def getPage(url , rule):
    g = grabber()
    return etree.HTML(g.sendRquest(url).text).xpath(rule)
    
start()