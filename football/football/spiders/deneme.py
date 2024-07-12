import time
import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
import time

class MatchspiderSpider(scrapy.Spider):
    name = "passspider"
    def start_requests(self):
       url = 'https://www.besoccer.com/livescore/2024-06-21'
       yield scrapy.Request(url, dont_filter=True,   meta=dict(
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

        liste = ['https://www.besoccer.com/Competition/super_lig',
                 'https://www.besoccer.com/Competition/premier_league',
                 'https://www.besoccer.com/Competition/primera_division',
                 'https://www.besoccer.com/Competition/serie_a',
                 'https://www.besoccer.com/Competition/segunda_division',
                 'https://www.besoccer.com/Competition/1_lig_turkey',
                 'https://www.besoccer.com/Competition/serie_a_brazil',
                 'https://www.besoccer.com/Competition/ligue_2',
                 'https://www.besoccer.com/Competition/eredivisie',
                 'https://www.besoccer.com/Competition/super_league_greece',
                 'https://www.besoccer.com/Competition/super_league_switzerland',
                 'https://www.besoccer.com/Competition/serie_b',
                 'https://www.besoccer.com/Competition/2_liga',
                 'https://www.besoccer.com/Competition/pro_league_belgium',
                 'https://www.besoccer.com/Competition/bundesliga',
                 'https://www.besoccer.com/Competition/championship',
                 'https://www.besoccer.com/Competition/champions_league',
                 'https://www.besoccer.com/Competition/europa_league',
                 'https://www.besoccer.com/Competition/conference-league',
                 'https://www.besoccer.com/Competition/premier-league-ukraine',
                 "https://www.besoccer.com/Competition/primeira_liga",
                 "https://www.besoccer.com/Competition/mls",
                 "https://www.besoccer.com/Competition/euro", 
                 "https://www.besoccer.com/Competition/copa_america",
                 "https://www.besoccer.com/Competition/world_cup",
                 "https://www.besoccer.com/Competition/africa_cup_of_nations"
                 ]
        

        hiddenPanels = response.css('div.panel.hiddenPanel')
        panels = response.css('div.panel')
      
        for hiddenPanel in hiddenPanels : 
            if hiddenPanel.css('a::attr(href)').get() in liste : 
                matches = hiddenPanel.css('a[href^="https://www.besoccer.com/match"]::attr(href)').getall()
                for match in matches :
                    yield response.follow(match, dont_filter=True, callback= self.parse_match_page)
        
        for panel in panels : 
            if panel.css('a::attr(href)').get() in liste : 
                soccers = panel.css('a[href^="https://www.besoccer.com/match"]::attr(href)').getall()
                for soccer in soccers : 
                    yield response.follow(soccer, dont_filter=True, callback= self.parse_match_page)

        next_page = response.css('li.tab a ::attr(href)')[2].get() #->'https://www.besoccer.com/livescore/...'
# and i or yaptım 
        if (next_page is not None) and (next_page != 'https://www.besoccer.com/livescore/2014-09-20') :
            yield scrapy.Request(next_page, dont_filter=True, meta=dict(
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
        all_tr = response.css('table.table tr')

        deneme['Date'] = response.css('div.date.header-match-date::text').get().strip()
        deneme['HomeTeam'] = response.css('div.name-box:nth-of-type(1)  a::text').get() 
        deneme['AwayTeam'] = response.css('div.name-box:nth-of-type(2)  a::text').get() 
    # Paslara özel script 
        for tr in all_tr :          
            if len(tr.css('td::text').getall()) != 0 :
                if (tr.css('td::text').getall()[1].strip() == 'Total Passes') or  (tr.css('td::text').getall()[1].strip() == 'Passes') or (tr.css('td::text').getall()[1].strip() == 'Accurate Passes') or (tr.css('td::text').getall()[1].strip() == 'Accurate Passes Percentage'): 
                    
                    stat = tr.css('td::text').getall()[1].strip()
                    home_value = tr.css('span ::text').getall()[0] 
                    away_value = tr.css('span ::text').getall()[1] 
                    deneme['Total Passes_away'] = away_value
                    deneme[f'{stat}_home'] = home_value
                    deneme[f'{stat}_away'] = away_value

                elif tr.css('td::text').getall()[1].strip() == 'Completed Passes' and len(tr.css('span ::text').getall()) == 4 : 

                    home_value = tr.css('span ::text').getall()[0] 
                    away_value = tr.css('span ::text').getall()[2] 
                    home_accu_value = tr.css('span ::text').getall()[1] 
                    away_accu_value = tr.css('span ::text').getall()[3]
                    deneme['Completed Passes_home'] = home_value
                    deneme['Completed Passes_away'] = away_value
                    deneme['Passes Accuracy_home'] = home_accu_value
                    deneme['Passes Accuracy_away'] = away_accu_value

                                   
        yield  deneme 

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
