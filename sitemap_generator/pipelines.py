# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import Encoder


class CrawlTestPipeline:
    def process_item(self, item, spider):
        # print(item)
        return item


class SitemapGeneratorScrapyPipeline(object):
    items = []

    def process_item(self, item, spider):
        index = len(self.items)
        if index > 0 and item.get("URL") == self.items[0].get("URL"):
            return
        self.items.append(item._values)
        return item

    def close_spider(self, spider, reason=None):
        list_url = []
        encode_url = (
            urlsafe_b64encode(spider.base_url.encode("utf-8"))
            .decode("utf-8")
            .rstrip("=")
        )

        file_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = os.path.abspath(file_dir)

        result_file_dir = os.path.join(root_dir, "..", f"db/crawl_{encode_url}.json")

        try:
            if os.path.isfile(result_file_dir):
                with open(result_file_dir, "r") as f_in:
                    list_url = json.loads(f_in.read())
                    list_url = list_url if list_url and len(list_url) > 0 else []
        except Exception as e:
            print("Error reading", e)

        with open(result_file_dir, "w") as f_out:
            for item in self.items:
                list_url.append(item["URL"])

            json.dump(
                list(set(list_url)), f_out, ensure_ascii=False, indent=4, cls=Encoder
            )
        pass
