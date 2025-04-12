import scrapy
from ekantipur_scraper.items import EkantipurItem
from bs4 import BeautifulSoup
import re

class EkantipurSpider(scrapy.Spider):
    name = "ekantipur"
    allowed_domains = ["ekantipur.com"]
    # Expanded list of categories
    start_urls = [
        "https://ekantipur.com/business/",
        "https://ekantipur.com/world/",
        "https://ekantipur.com/sports/",
        "https://ekantipur.com/national/",
        "https://ekantipur.com/opinion/",
        "https://ekantipur.com/entertainment/",
        "https://ekantipur.com/education/",
        "https://ekantipur.com/blog/",
    ]

    # Track scraped URLs to avoid duplicates
    def __init__(self, *args, **kwargs):
        super(EkantipurSpider, self).__init__(*args, **kwargs)
        self.scraped_urls = set()

    # Function to check if text is in Nepali (Devanagari script)
    def is_nepali(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def parse(self, response):
        # Extract category from URL
        category = response.url.split("/")[-2]
        
        # Parse the listing page
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.select(".normal"):
            title = row.find("h2")
            if title and title.a:
                title_text = title.text.strip()
                title_link = title.a.get("href")
                if not title_link.startswith("https"):
                    title_link = "https://ekantipur.com" + title_link
                
                # Skip if already scraped
                if title_link in self.scraped_urls:
                    continue
                self.scraped_urls.add(title_link)
                
                # Yield a request to the article page
                yield scrapy.Request(
                    url=title_link,
                    callback=self.parse_article,
                    meta={
                        'title': title_text,
                        'url': title_link,
                        'category': category
                    }
                )

        # Handle pagination
        next_page = soup.select_one("a.next")
        if next_page and next_page.get("href"):
            next_url = "https://ekantipur.com" + next_page.get("href")
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_article(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data from article page
        item = EkantipurItem()
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['category'] = response.meta['category']

        # Date from <span class="published-at">
        date_elem = soup.find("span", class_="published-at")
        item['date'] = date_elem.text.strip() if date_elem else "Date not found"

        # Description from <div class="description current-news-block">
        description_block = soup.find("div", class_="description current-news-block")
        description_text = ""
        if description_block:
            paragraphs = description_block.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if self.is_nepali(text):
                    description_text += text + " "
            item['description'] = description_text.strip() or "No Nepali description available"
        else:
            item['description'] = "Description block not found"

        # Author
        author_elem = soup.select_one(".author")
        if author_elem and author_elem.a:
            item['author_url'] = author_elem.a.get("href")
            item['author'] = author_elem.text.strip()
        else:
            item['author_url'] = "Author URL not found"
            item['author'] = "Unknown Author"

        # Content
        news_content = ""
        content_container = soup.select_one(".row")
        if content_container:
            for content in content_container.find_all("p"):
                content_parts = str(content).split(">")
                if len(content_parts) > 1:
                    content_text = content_parts[1].split("<")[0].strip()
                    if len(content_text) == 0:
                        break
                    else:
                        news_content += content_text + " "
            item['content'] = news_content.strip()
        else:
            item['content'] = "Content not found"

        yield item