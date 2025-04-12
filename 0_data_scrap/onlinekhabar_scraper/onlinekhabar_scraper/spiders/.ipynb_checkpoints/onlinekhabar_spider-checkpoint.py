import scrapy
from onlinekhabar_scraper.items import OnlinekhabarItem
import re

class OnlinekhabarSpider(scrapy.Spider):
    name = "onlinekhabar"
    allowed_domains = ["www.onlinekhabar.com"]
    start_urls = [
        "https://www.onlinekhabar.com/content/news",  # Samachar (News)
        "https://www.onlinekhabar.com/business",      # Business
        "https://www.onlinekhabar.com/markets",       # Share Markets
        "https://www.onlinekhabar.com/health",        # Health
        "https://www.onlinekhabar.com/lifestyle",     # Lifestyle
        "https://www.onlinekhabar.com/entertainment", # Entertainment
        "https://www.onlinekhabar.com/sports",        # Sports
        "https://www.onlinekhabar.com/opinion",       # Opinion
        "https://www.onlinekhabar.com/rashifal",      # Rashifal
    ]

    def __init__(self, *args, **kwargs):
        super(OnlinekhabarSpider, self).__init__(*args, **kwargs)
        self.scraped_urls = set()  # Track scraped article URLs to avoid duplicates

    # Function to check if text is in Nepali (Devanagari script)
    def is_nepali(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def parse(self, response):
        # Extract category from URL
        category = response.url.split("/")[-1] or "unknown"

        # Extract article links from category page
        for news in response.css("div.ok-news-post.ok-card-post"):
            article_url = news.css("a::attr(href)").get()
            if article_url and article_url not in self.scraped_urls:
                self.scraped_urls.add(article_url)
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    meta={'category': category}
                )

        # Follow sidebar category links (optional, for completeness)
        sidebar_links = response.css("div.ok-side-menu-items ul li a::attr(href)").getall()
        for link in sidebar_links:
            if link.startswith("https://www.onlinekhabar.com") and link not in self.start_urls:
                yield scrapy.Request(url=link, callback=self.parse)

        # Pagination (if exists, inspect live site for "Next" button)
        # Example (hypothetical):
        # next_page = response.css("a.next-page::attr(href)").get()
        # if next_page:
        #     yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_article(self, response):
        # Initialize item
        item = OnlinekhabarItem()
        item['title'] = response.css("h1.ok-post-title::text").get(default="No title found").strip()
        item['url'] = response.url
        item['category'] = response.meta['category']
        item['image'] = response.css("div.ok-post-detail-featured-img img::attr(src)").get(default="No image found")

        # Extract Nepali text from <div class="ok18-single-post-content-wrap">
        content_wrap = response.css("div.ok18-single-post-content-wrap")
        nepali_content = []
        for paragraph in content_wrap.css("p::text").getall():
            text = paragraph.strip()
            if self.is_nepali(text) and text:  # Only include non-empty Nepali text
                nepali_content.append(text)

        item['description'] = " ".join(nepali_content) if nepali_content else "No Nepali content found"

        yield item