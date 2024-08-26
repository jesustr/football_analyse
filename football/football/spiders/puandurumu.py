import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
 

#*** UZAYAN ŞAMPİYONLAR LİGİ MAÇLARININ SKORLARINI YANLIŞ ALIYOR DÜZELT***
class PuandurumuSpider(scrapy.Spider):
    name = "puandurumu"
    allowed_domains = ["www.sofascore.com"]
    
    def start_requests(self):    
        with open('/Users/icy/Desktop/scrapping_scrapy_football/football/football/spiders/sofa_temiz_urls/puandurumu_unscraped.txt', 'r') as file:
            urls = file.readlines()
             # Bin bin seçerek devam et,  yüksek seçimler sıknııtılı ram yetmiyor gibi sorunlar çıkıyor.
            for url in urls:  
                url.strip()
                yield scrapy.Request(url, meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod("evaluate", "for (let i = 0; i < 1; i++) setTimeout(() => window.scrollBy(0, 3000), i * 2000);"),
                        PageMethod("wait_for_timeout", 5000), 
                        #PageMethod("wait_for_selector", "div.Box.BwRpA", timeout=10000),
                        #PageMethod("evaluate", "for (let i = 0; i < 6; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                        #PageMethod("click", selector = "div.Box.dktgmV>span.Text.crNdjU", button = 'left'),          
                        
                ],
                errback=self.errback,
                )) 
        

    async def parse(self,response):
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.
        
        parse = {} 
        if response.css('div.Box.clAhaB.Col.gcPBSH>div:nth-child(3)>div.Box.gPbxDB>div.Box.jilUFb>div.Box.klGMtt>div.Box.iHEIFv>div.TabPanel.bpHovE>div'):
            puan_durumu_takimlar = response.css('div.Box.clAhaB.Col.gcPBSH>div:nth-child(3)>div.Box.gPbxDB>div.Box.jilUFb>div.Box.klGMtt>div.Box.iHEIFv>div.TabPanel.bpHovE>div')
        else :
            puan_durumu_takimlar = response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.clAhaB.Col.gcPBSH>div:nth-child(3)>div.Box.gPbxDB>div.Box.jilUFb>div.Box.klGMtt>div.Box.Flex.hVZxjR.cQgcrM>div')
        siralar = puan_durumu_takimlar.css('a>div>div:nth-child(1)> ::text').getall() #>div.Box.Flex.kQcHaX.jLRkRA.sc-ihgnxF.kJqYUe>div:nth-child(1)
        takimlar = puan_durumu_takimlar.css('a>div>div.Box.ljKzDM ::text').getall()
        puanlar = puan_durumu_takimlar.css('a>div>div:last-child>bdi div::text').getall()
        sol__  =  response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.kVEXeF>div.Box.jJMKoa>div.Box.Flex.dZNeJi.bnpRyo') 
        home_team = sol__.css('div:nth-child(1) bdi ::text').get()
        away_team = sol__.css('div:nth-child(3) bdi ::text').get()    
        try:
            for index , takim in enumerate(takimlar) : 
                    if home_team == takim : 
                        parse['point_home'] = puanlar[index]
                        parse['place_home'] = siralar[index]
                    elif away_team == takim :
                        parse['point_away'] = puanlar[index]
                        parse['place_away'] = siralar[index]


        except IndexError  :
            parse['error'] = response.url
        yield parse 
 
    

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

