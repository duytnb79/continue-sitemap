from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from ..items import PageInfoItem
from scrapy.http import Request
from scrapy.selector import Selector
import re
import zlib
from scrapy.exceptions import IgnoreRequest


class LinkExtractorSpiderBase(CrawlSpider):
    name = "link_extractor_spider"
    http_user = ""
    http_pass = ""

    def parse_start_url(self, response):
        return self.parse_pageinfo(response)

    def parse_pageinfo(self, response):
        if response.headers.get("Content-Type"):
            content_type = response.headers["Content-Type"].decode("utf-8")
            if "text/html" not in content_type:
                msg = "Not allow Content-Type: {}".format(content_type)
                raise IgnoreRequest(msg)
        if response.url and (not self.rules[0].link_extractor.matches(response.url)):
            return None
        sel = Selector(response)
        item = PageInfoItem()
        item["URL"] = response.url
        item["title"] = sel.xpath("/html/head/title/text()").extract()
        item["meta"] = sel.xpath("/html/head/meta").getall()
        item["h1"] = "".join(sel.xpath("//h1/descendant::text()").extract()).strip()
        # item["html_compressed_bytes"] = zlib.compress(response.text.encode("utf-8"))

        if ("iframe" in response.meta) and self.is_all_page:
            iframe_links = LinkExtractor(
                allow=("^" + re.escape(self.base_url)),
                allow_domains=self.allowed_domains,
            ).extract_links(response)
            for link in iframe_links:
                yield Request(link.url, callback=self.parse_pageinfo)

        ext_iframe = sel.xpath("//iframe/@src").extract()
        for iframe in ext_iframe:
            iframe_url = response.urljoin(iframe)
            yield Request(
                iframe_url, callback=self.parse_pageinfo, meta={"iframe": True}
            )
        yield item


class LinkExtractorSpiderClassFactory:
    @staticmethod
    def create_class(
        allowed_domains: list,
        start_urls: list,
        base_url="",
        basic_auth_username="",
        basic_auth_password="",
        is_all_page=False,
    ):
        class LinkExtractorSpider(LinkExtractorSpiderBase):
            pass

        if len(start_urls) > 1:
            urls_allow = []
            for full_url in start_urls:
                urls_allow.append("^" + re.escape(full_url) + "$")
            base_url = full_url
            LinkExtractorSpider.allowed_domains = allowed_domains
            LinkExtractorSpider.start_urls = start_urls
            LinkExtractorSpider.base_url = base_url

            if len(basic_auth_username) > 0 and len(basic_auth_password) > 0:
                LinkExtractorSpider.http_user = basic_auth_username
                LinkExtractorSpider.http_pass = basic_auth_password
            base_url_formatted = base_url
            LinkExtractorSpider.rules = [
                Rule(
                    LinkExtractor(allow=(urls_allow), unique=True, tags=(), attrs=()),
                    callback="parse_pageinfo",
                    follow=True,
                )
            ]
        else:
            LinkExtractorSpider.allowed_domains = allowed_domains
            LinkExtractorSpider.start_urls = start_urls
            LinkExtractorSpider.base_url = base_url

            if len(basic_auth_username) > 0 and len(basic_auth_password) > 0:
                LinkExtractorSpider.http_user = basic_auth_username
                LinkExtractorSpider.http_pass = basic_auth_password
            base_url_formatted = base_url
            if is_all_page:
                if "index.html" in base_url:
                    base_url_formatted = re.sub(r"(index\.html(\?.*)*$)", "", base_url)
                elif ".html" in base_url:
                    base_url_formatted = re.sub(r"(\.html(\?.*)*$)", "", base_url)
            urls_allow = []
            urls_allow.append("^" + re.escape(base_url_formatted))
            LinkExtractorSpider.rules = [
                Rule(
                    LinkExtractor(allow=(urls_allow)),
                    callback="parse_pageinfo",
                    follow=True,
                )
            ]
            if not is_all_page:
                LinkExtractorSpider.rules = [
                    Rule(
                        LinkExtractor(
                            allow=("^" + re.escape(base_url_formatted)),
                            tags=(),
                            attrs=(),
                        ),
                        callback="parse_pageinfo",
                        follow=True,
                    )
                ]
        return LinkExtractorSpider
