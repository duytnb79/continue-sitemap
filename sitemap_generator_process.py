import os
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse
from sitemap_generator.spiders.link_extractor_spider import (
    LinkExtractorSpiderClassFactory,
)

# from scrapy.resolver import CachingThreadedResolver
# from scrapy.utils.datatypes import LocalCache
# from twisted.internet import defer


class SitemapGeneratorProcess(CrawlerProcess):
    items: list = []

    def __init__(
        self,
        allowed_domains=[],
        start_urls=[],
        base_url="",
        basic_auth_username="",
        basic_auth_password="",
        is_all_page=False,
        ip_address="",
    ):
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.base_url = base_url

        # The path seen from root, ie. from main.py
        settings_file_path = "sitemap_generator.settings"
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", settings_file_path)
        default_setting = get_project_settings()
        default_version = "105.0.5195.127"
        try:
            latest_version = requests.get(
                "https://omahaproxy.appspot.com/win", timeout=5
            ).text
            check_version = int(latest_version.replace(".", ""))
            default_version = latest_version
        except:
            pass
        new_ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{default_version} Safari/537.36"
        default_setting["USER_AGENT"] = new_ua
        default_setting["DEFAULT_REQUEST_HEADERS"]["User-Agent"] = new_ua

        default_setting["CONCURRENT_REQUESTS"] = 64
        default_setting["CONCURRENT_ITEMS"] = 100
        default_setting["CONCURRENT_REQUESTS_PER_DOMAIN"] = 64
        default_setting["CONCURRENT_REQUESTS_PER_IP"] = 100
        # default_setting["REACTOR_THREADPOOL_MAXSIZE"] = 10
        # default_setting["AUTOTHROTTLE_ENABLED"] = True
        # default_setting["AUTOTHROTTLE_DEBUG"] = True

        # if ip_address:
        #     os.environ["VERIFY_BY_IP"] = ip_address if ip_address else ""
        #     os.environ["MAIN_HOST"] = (
        #         allowed_domains[0]
        #         if len(allowed_domains) > 0
        #         else urlparse(base_url).netloc
        #     )

        super().__init__(default_setting)

        self.crawl(
            LinkExtractorSpiderClassFactory.create_class(
                allowed_domains=allowed_domains,
                start_urls=start_urls,
                base_url=base_url,
                basic_auth_username=basic_auth_username,
                basic_auth_password=basic_auth_password,
                is_all_page=is_all_page,
            )
        )
        for c in self.crawlers:
            c.runner = self
        pass


# class CustomIPResolver(CachingThreadedResolver):
#     def getHostByName(self, name, timeout=None):
#         custom_ip_address = os.environ.get("VERIFY_BY_IP", "")
#         main_host = os.environ.get("MAIN_HOST", "")

#         if len(main_host) > 0 and len(custom_ip_address) > 0:
#             return defer.succeed(custom_ip_address)

#         return super().getHostByName(name, timeout)
