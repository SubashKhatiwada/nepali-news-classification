import os

class EkantipurPipeline:
    def open_spider(self, spider):
        self.base_dir = "ekantipur_news"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def process_item(self, item, spider):
        # Create category folder
        category_dir = os.path.join(self.base_dir, item['category'])
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        # Create a safe filename
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in item['title'])[:50]
        file_name = f"{safe_title}_{len(os.listdir(category_dir))}.txt"
        file_path = os.path.join(category_dir, file_name)

        # Write to text file
        with open(file_path, 'w', encoding='utf-8') as f:
            # f.write(f"Title: {item['title']}\n")
            # f.write(f"URL: {item['url']}\n")
            # f.write(f"Date: {item['date']}\n")
            # f.write(f"Author: {item['author']}\n")
            # f.write(f"Author URL: {item['author_url']}\n")
            # f.write(f"Category: {item['category']}\n")
            f.write(f"{item['description']}\n")
            # f.write(f"Content: {item['content']}\n")

        spider.logger.info(f"Saved article to {file_path}")
        return item