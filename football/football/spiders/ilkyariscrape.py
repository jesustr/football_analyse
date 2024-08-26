import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
# scrape ederken url leride scrape edip sonra bu urlerden liste yapıp hepsinin içinde dönerek oranları burdan scrape et.
class IlkyariscrapeSpider(scrapy.Spider):
    name = "ilkyariscrape"
    allowed_domains = ["www.sofascore.com"]   
    def start_requests(self):    
        with open('/Users/icy/Desktop/scrapping_scrapy_football/football/football/spiders/sofa_temiz_urls/filtered_week_match_links_unscraped.txt', 'r') as file:
            urls = file.readlines()
             # Bin bin seçerek devam et,  yüksek seçimler sıknııtılı ram yetmiyor gibi sorunlar çıkıyor.
            for url in urls:  
                url.strip()
                yield scrapy.Request(url, meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod("evaluate", "for (let i = 0; i < 1; i++) setTimeout(() => window.scrollBy(0, 3000), i * 2000);"),
                        PageMethod("wait_for_timeout", 4000), 
                        PageMethod("click", selector = "div.Box.ekBGbr>div:nth-child(2) ", button = 'left'),          
                        #PageMethod("wait_for_selector", "div.Box.BwRpA", timeout=10000),
                        #PageMethod("evaluate", "for (let i = 0; i < 6; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),                
                 ],
                errback=self.errback,
                )) 
        
    async def parse(self,response):
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.
        parse = {}
        try :     
            for j in range(1,3):                
                statistics_list = response.css(f'div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.cYKaoH>div.Box.klGMtt>div.Box.fNqMCK>div.TabPanel.bpHovE>div.Box.BwRpA>div:nth-child({j}) span::text').getall()
                statistics_list = statistics_list[1:] #listenin başında gereksiz birşey vardı onu çıkardım loopa sokabilcek şekle geldi.
                for i in range(0,len(statistics_list),3):
                    parse[f'{statistics_list[i+1]}_home_firsthalf'] = statistics_list[i]
                    parse[f'{statistics_list[i+1]}_away_firsthalf'] = statistics_list[i+2]
            parse['match_link'] = response.url
        except  IndexError :
            parse['date'] = None 

        yield parse 

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

