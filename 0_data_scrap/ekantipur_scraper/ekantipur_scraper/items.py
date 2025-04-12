import scrapy

class EkantipurItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    author = scrapy.Field()
    author_url = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()