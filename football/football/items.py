# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FootballItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class FbrefItem(scrapy.Item):
    
    pass
    date = scrapy.Field()
    league = scrapy.Field()
    match_week = scrapy.Field()
    home_team = scrapy.Field()
    away_team = scrapy.Field()
    home_goal = scrapy.Field()
    away_goal = scrapy.Field()
    home_firsth_goals = scrapy.Field()
    away_firsth_goals = scrapy.Field()
    home_corners = scrapy.Field()
