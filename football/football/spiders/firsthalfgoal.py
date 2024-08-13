import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
 

# scrape ederken url leride scrape edip sonra bu urlerden liste yapıp hepsinin içinde dönerek oranları burdan scrape et.
class FirsthalfgoalSpider(scrapy.Spider):
    name = "firsthalfgoal"
    allowed_domains = ["www.sofascore.com"]
    
    def start_requests(self):    
        with open('/Users/icy/Desktop/scrapping_scrapy_football/football/football/spiders/sofa_temiz_urls/son_eksik_maclar_unscraped.txt', 'r') as file:
            urls = file.readlines()
             # Bin bin seçerek devam et,  yüksek seçimler sıknııtılı ram yetmiyor gibi sorunlar çıkıyor.
            for url in urls:  
                url.strip()
                yield scrapy.Request(url, meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod("evaluate", "for (let i = 0; i < 1; i++) setTimeout(() => window.scrollBy(0, 3000), i * 2000);"),
                        #PageMethod("wait_for_selector", "div.Box.BwRpA", timeout=10000),
                        #PageMethod("evaluate", "for (let i = 0; i < 6; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                        PageMethod("wait_for_timeout", 4000), 
                        #PageMethod("click", selector = "div.Box.dktgmV>span.Text.crNdjU", button = 'left'),          
                        
                ],
                errback=self.errback,
                )) 
        
    async def parse(self,response):
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.
        parse = {}

   
        try :
            sol = response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.kVEXeF>div.Box.gWLjoE>div.Box.gIGhov>div.Box.klGMtt>div.Box.klGMtt>div.Box.cNWmcN>div.Box.dPiYzr>div.Text.fVXooM ::text').getall()[-1].replace('HT','').strip()
            parse['home_iy_goal'] = sol[0]
            parse['away_iy_goal'] = sol[-1]
        except  IndexError :
            parse['date'] = None     
        parse['match_link'] = response.url
        
        yield parse 



    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

