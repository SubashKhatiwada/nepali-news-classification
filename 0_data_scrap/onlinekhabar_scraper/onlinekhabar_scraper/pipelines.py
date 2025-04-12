import os

class OnlinekhabarPipeline:
    def open_spider(self, spider):
        self.base_dir = "onlinekhabar_news"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def process_item(self, item, spider):
        category_dir = os.path.join(self.base_dir, item['category'])
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in item['title'])[:50]
        file_name = f"{safe_title}_{len(os.listdir(category_dir))}.txt"
        file_path = os.path.join(category_dir, file_name)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # f.write(f"Title: {item['title']}\n")
                # f.write(f"URL: {item['url']}\n")
                # f.write(f"Category: {item['category']}\n")
                # f.write(f"Image: {item['image']}\n")
                f.write(f"{item['description']}\n")
            spider.logger.info(f"Saved article to {file_path}")
        except Exception as e:
            spider.logger.error(f"Failed to save {item['title']} to {file_path}: {str(e)}")

        return item