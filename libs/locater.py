from lxml import etree

class locater :
    
    def xpath(self , htmlText , rule):
        #先将其解释为html
        html = etree.HTML(htmlText)
        return html.xpath(rule)