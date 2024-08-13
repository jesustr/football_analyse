import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
 

#*** UZAYAN ŞAMPİYONLAR LİGİ MAÇLARININ SKORLARINI YANLIŞ ALIYOR DÜZELT***
class DenemesofaSpider(scrapy.Spider):
    name = "denemesofa"
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
                        PageMethod("wait_for_timeout", 8000), 
                        #PageMethod("click", selector = "div.Box.dktgmV>span.Text.crNdjU", button = 'left'),          
                        
                ],
                errback=self.errback,
                )) 
        

    async def parse(self,response):
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.
        parse = {}
        #--------
        sol  =  response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.jfBWUX>div.Box.Flex.dlyXLO.jLRkRA>div.Box.Flex.bttEbg.crsNnE>span.Text.bkqxZg ::text')
        try :
            parse['date'] = sol.getall()[0].replace('/','-')
        except  IndexError :
            parse['date'] = None 
        try :
            parse['hour'] = sol.getall()[1]
        except  IndexError :  
            parse['hour'] = None
        #--------
        sol2 = response.css('ul.BreadcrumbContent.gWYkXa')
        try : 
            parse['ulke'] = sol2.css('li:nth-child(2) ::text').get() 
        except  IndexError :
            parse['ulke'] = None
        try:
            parse['Organizasyon'] = sol2.css('li:nth-child(3) ::text').get() #lig
        except IndexError : 
            parse['Organizasyon'] = None
        try: 
            parse['Org_detay'] = sol2.css('li:nth-child(3) ::text').getall()[2]
        except IndexError : 
            parse['Org_detay'] = None
        #--------
        sol3  =  response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.kVEXeF>div.Box.jJMKoa>div.Box.Flex.dZNeJi.bnpRyo') 
        try : 
            parse['Home_team'] = sol3.css('div:nth-child(1) bdi ::text').get()
        except IndexError : 
            parse['Home_team'] = None
        try : 
            parse['Away_team'] = sol3.css('div:nth-child(3) bdi ::text').get()
        except IndexError :
            parse['Away_team'] = None    
        try: 
            parse['Home_goal'] = sol3.css('div.Box.dUMdHh span::text').getall()[0]
        except IndexError :
            parse['Home_goal'] = None
        try : 
            parse['Away_goal'] = sol3.css('div.Box.dUMdHh span::text').getall()[2]
        except : 
            parse['Away_goal'] = None
        #---------
        parse['referee'] = None
        parse['red_card_avg'] = None
        parse['yellow_card_avg'] = None
        
        referee_data = response.css('div.Box.jfBWUX>a[href*="referee"]>div.Box.Flex.mMMTG.jLRkRA>div.Box.Flex.bttEbg.crsNnE span::text').getall()
        if len(referee_data) > 1:
            parse['referee'] = referee_data[1]
        
        card_data = response.css('div.Box.jfBWUX>a[href*="referee"]>div.Box.Flex.mMMTG.jLRkRA>div.Box.Flex.bttEbg.crsNnE>div.Text.ipQGqf::text').getall()
        if len(card_data) >= 3:
            parse['red_card_avg'] = card_data[1]
            parse['yellow_card_avg'] = card_data[2]
        #---------   
        try : 
            statistics_list = response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.cYKaoH>div.Box.klGMtt>div.Box.fNqMCK>div.TabPanel.bpHovE>div.Box.BwRpA>div:nth-child(1) span::text').getall()
            statistics_list = statistics_list[1:] #listenin başında gereksiz birşey vardı onu çıkardım loopa sokabilcek şekle geldi.
            for i in range(0,len(statistics_list),3):
                parse[f'{statistics_list[i+1]}_home'] = statistics_list[i]
                parse[f'{statistics_list[i+1]}_away'] = statistics_list[i+2]
        except IndexError :
            parse['statistik'] = 'Hata'
        try : 
            statistics_list = response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.cYKaoH>div.Box.klGMtt>div.Box.fNqMCK>div.TabPanel.bpHovE>div.Box.BwRpA>div:nth-child(2) span::text').getall()
            statistics_list = statistics_list[1:] #listenin başında gereksiz birşey vardı onu çıkardım loopa sokabilcek şekle geldi.
            for i in range(0,len(statistics_list),3):
                parse[f'{statistics_list[i+1]}_home'] = statistics_list[i]
                parse[f'{statistics_list[i+1]}_away'] = statistics_list[i+2]
        except IndexError :
            parse['statistik'] = 'Hata'

        try :
            sol4 = response.css('div.Box.cyOxcH.Page.eWDDro>div.Box.Flex.ggRYVx.cQgcrM.Grid.dRBNa>div.Box.kUNcqi.Col.cxAhno>div.Box.kVEXeF>div.Box.gWLjoE>div.Box.gIGhov>div.Box.klGMtt>div.Box.klGMtt>div.Box.cNWmcN>div.Box.dPiYzr>div.Text.fVXooM ::text').getall()[-1].replace('HT','').strip()
            parse['home_iy_goal'] = sol4[0]
            parse['away_iy_goal'] = sol4[-1]
        except  IndexError :
            parse['date'] = None     
        
        parse['match_link'] = response.url
        
        yield parse 
 
    

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

