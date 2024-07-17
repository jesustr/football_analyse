import time
import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
import time

class MatchspiderSpider(scrapy.Spider):
    name = "matchspider"
    def start_requests(self):
       url = 'https://www.besoccer.com/livescore/2024-07-15'
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
        event_panels = response.css('#mod_events .match-events #orderEvent > .panel')
        deneme['Date'] = response.css('div.date.header-match-date::text').get().strip()
        deneme['HomeTeam'] = response.css('div.name-box:nth-of-type(1)  a::text').get() 
        
        for event_panel in event_panels:
            if event_panel.css('::text').getall()[1] == 'Goals':
                goal_sections = event_panel.css('.panel-body.table-list>.table-body.pn>.table-played-match')
                left_ilk_counter = 0
                right_ilk_counter = 0
                for goal_section in goal_sections:

                    if '+' in goal_section.css('.col-mid-rows>.min  ::text').get() :
                        goal_minute = float(goal_section.css('.col-mid-rows>.min  ::text').get()[:2])
                    else :
                        goal_minute = float(goal_section.css('.col-mid-rows>.min  ::text').getall()[0].replace("'",""))
                    
                    if (len(goal_section.css('.col-side.left').get()) >= 200) and goal_minute < 46 :
                        left_ilk_counter += 1 
                    elif (len(goal_section.css('.col-side.left').get()) < 200) and goal_minute < 46 :
                        right_ilk_counter += 1         
       
                    #elif (len(goal_section.css('.col-side.left').get()) < 200) and goal_minute > 45 :
                deneme['fhalf_goal_home'] = left_ilk_counter
                deneme['fhalf_goal_away'] = right_ilk_counter
                   
        yield  deneme 

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()



    # event_panels = response.css('#mod_events .match-events #orderEvent > .panel')
    # event_panels[0].css('::text').getall()[1] -> 'Goals'
    # event_panels[1].css('::text').getall()[1] -> 'Substıtutıons'
    # goal_section = event_panels[0]
    # goal_section.css('.panel-body.table-list>.table-body.pn>.table-played-match') -> gollerin rowları
    # first_row = goal_section.css('.panel-body.table-list>.table-body.pn>.table-played-match')[0] ilk row 
    # len(first_row.css('.col-side>div').getall()) #-> sağ tarafın div sayısı
    # goal_section.css('.col-mid-rows>.min  ::text').getall()[0].replace("'","") -> gol dakikası
    # dikkatli yap . lar divler karışmasın
    # len(goal_section.css('.col-side.left').get()) #-> gol sağmı solmu
    