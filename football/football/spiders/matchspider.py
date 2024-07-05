import time
import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
import time

class MatchspiderSpider(scrapy.Spider):
    name = "matchspider"
    def start_requests(self):
       url = 'https://www.besoccer.com/livescore/2015-07-08'
       yield scrapy.Request(url, meta=dict(
				playwright = True,
				playwright_include_page = True, 
	    		playwright_page_methods =[ 
                    PageMethod("evaluate", "for (let i = 0; i < 6; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                    PageMethod("wait_for_timeout", 12000),          
          ],
        errback=self.errback,
		))
    
    async def parse(self,response):      
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.

        liste = ['https://www.besoccer.com/competition/super_lig',
                 'https://www.besoccer.com/competition/premier_league',
                 'https://www.besoccer.com/competition/primera_division',
                 'https://www.besoccer.com/competition/serie_a',
                 'https://www.besoccer.com/competition/segunda_division',
                 'https://www.besoccer.com/competition/1_lig_turkey',
                 'https://www.besoccer.com/competition/serie_a_brazil',
                 'https://www.besoccer.com/competition/ligue_2',
                 'https://www.besoccer.com/competition/eredivisie',
                 'https://www.besoccer.com/competition/super_league_greece',
                 'https://www.besoccer.com/competition/super_league_switzerland',
                 'https://www.besoccer.com/competition/serie_b',
                 'https://www.besoccer.com/competition/2_liga',
                 'https://www.besoccer.com/competition/pro_league_belgium',
                 'https://www.besoccer.com/competition/bundesliga',
                 'https://www.besoccer.com/competition/championship',
                 'https://www.besoccer.com/competition/champions_league',
                 'https://www.besoccer.com/competition/europa_league',
                 'https://www.besoccer.com/competition/conference-league',
                 'https://www.besoccer.com/competition/premier-league-ukraine',
                 "https://www.besoccer.com/competition/primeira_liga",
                 "https://www.besoccer.com/competition/mls",
                 "https://www.besoccer.com/Competition/euro", 
                 "https://www.besoccer.com/Competition/copa_america"]

        hiddenPanels = response.css('div.panel.hiddenPanel')
        panels = response.css('div.panel')
      
        for hiddenPanel in hiddenPanels : 
            if hiddenPanel.css('a::attr(href)').get() in liste : 
                matches = hiddenPanel.css('a[href^="https://www.besoccer.com/match"]::attr(href)').getall()
                for match in matches :
                    yield response.follow(match, callback= self.parse_match_page)
        
        for panel in panels : 
            if panel.css('a::attr(href)').get() in liste : 
                soccers = panel.css('a[href^="https://www.besoccer.com/match"]::attr(href)').getall()
                for soccer in soccers : 
                    yield response.follow(soccer, callback= self.parse_match_page)

        next_page = response.css('li.tab a ::attr(href)')[2].get() #->'https://www.besoccer.com/livescore/...'
# and i or yaptım 
        if (next_page is not None) or (next_page != 'https://www.besoccer.com/livescore/2014-12-31') :
            yield scrapy.Request(next_page, meta=dict(
				playwright = True,
				playwright_include_page = True, 
	    		playwright_page_methods =[
                    PageMethod("evaluate", "for (let i = 0; i < 3; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                    PageMethod("wait_for_timeout", 12000),
                    
          ],
        errback=self.errback,
		))
    
    async def parse_match_page(self,response) :

        deneme = {}
        stat_table = response.css('table.table')
        elements = response.css('table.table tr>td::text').getall() 
        all_tr = response.css('table.table tr')

        
        deneme['Date'] = response.css('div.date.header-match-date::text').get().strip()
        deneme['Competition'] = (response.css('section.match-header.fws-hide a::text').get()).strip() 
        deneme['HomeTeam'] = response.css('div.name-box:nth-of-type(1)  a::text').get() 
        deneme['AwayTeam'] = response.css('div.name-box:nth-of-type(2)  a::text').get() 
        deneme['HomeGoal'] = response.css('div.data span.r1::text').get()
        deneme['AwayGoal'] = response.css('div.data span.r2::text').get()
        
        for tr in all_tr :          
            if len(tr.css('td::text').getall()) != 0 : 
                if len(tr.css('td>p::text').getall()) != 0 :  
                   
                    #deneme[f'{stat}_2'] = away_value 
                    stat = tr.css('p::text').get()
                    home_value = tr.css('span ::text').getall()[0] 
                    away_value = tr.css('span ::text').getall()[1] 
                    deneme[f'{stat}_home'] = home_value
                    deneme[f'{stat}_away'] = away_value
                #total shoots ve ball possesion burdan geliyor 
                    
                elif len(tr.css('td::text').getall()[1].strip()) != 0 :

                    stat = tr.css('td::text').getall()[1].strip()
                    home_value = tr.css('td>div.td-num.left>span  ::text').get()
                    away_value = tr.css('td>div.td-num.right>span  ::text').get()
                    deneme[f'{stat}_home'] = home_value
                    deneme[f'{stat}_away'] = away_value
               
                else : 

                    deneme['off_target_home'] = tr.css('td>div.row.mv5>div:nth-child(1)>div>span ::text').getall()[0]
                    deneme['on_target_home'] = tr.css('td>div.row.mv5>div:nth-child(1)>div>span ::text').getall()[2]
                    deneme['off_target_away'] = tr.css('td>div.row.mv5>div:nth-child(2)>div>span ::text').getall()[1]
                    deneme['on_target_away'] = tr.css('td>div.row.mv5>div:nth-child(2)>div>span ::text').getall()[3]     

        yield  deneme 

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

