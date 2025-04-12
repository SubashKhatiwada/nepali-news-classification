import scrapy

class OnlinekhabarItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()