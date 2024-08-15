import scrapy 
from sys import path
from scrapy_playwright.page import PageMethod
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time

## 2024 U SCRAPE ETMEYE 27 JUNE DAN BAŞLADIM.
class MatchspiderSpider(scrapy.Spider):
    name = "fbrefscrape"  
    start_date = datetime(2024, 8, 12)
    end_date = datetime(2024, 8, 9 )

    def start_requests(self):    
        date = self.start_date  
        while date >= self.end_date : 
            date_str =  date.strftime('%Y-%m-%d') 
            url = f'https://www.sofascore.com/football/{date_str}'   #'https://www.sofascore.com/football/2024-05-08'
            yield scrapy.Request(url, meta=dict(
                        playwright = True,
                        playwright_include_page = True, 
                        playwright_page_methods =[ 
                            PageMethod("wait_for_timeout", 4000), 
                            PageMethod("evaluate", "for (let i = 0; i < 1; i++) setTimeout(() => window.scrollBy(0, 1350), i * 2000);"),
                            PageMethod("wait_for_selector", "div.Box.klGMtt", timeout=5000),
                ],
                errback=self.errback,
                ))

            date -= timedelta(days=1)

    #10761
    async def parse(self,response):
        page = response.meta['playwright_page']
        await page.close()  #async pagecoroutine calıssın diye.
        match_link = 'https://www.sofascore.com'
        parse = {}
        for product in response.css('div.Box.klGMtt'):          
            if product.css('a[href^="/football/match/"]'):
                match = match_link + product.css('a::attr(href)').get() 
                #parse['date'] = date_str
                parse['url'] = match 
                yield parse

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

   #             yield response.follow(match, callback= self.parse_match_page)
   

            # if product.css('a[href^="/football/match/"]'):
            #     yield {
            #         'urls' : match_link + product.css('a::attr(href)').get() 
            #     }
  
    # async def parse_match_page(self,response) :
    #     parse = {}
    #     parse['url'] = response.url
    #     yield parse

    # async def parse(self,response):
    #     page = response.meta['playwright_page']
    #     await page.close()  #async pagecoroutine calıssın diye.
    #     yield {
    #         'text' : response.text
    #     }
    
