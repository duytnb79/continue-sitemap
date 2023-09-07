import os
import shutil
import argparse
from urllib.parse import urlparse

from sitemap_generator_process import (
    SitemapGeneratorProcess,
)

file_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(file_dir)

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="")
parser.add_argument("--is-all-page", action="store_true")
parser.add_argument("--is-new-sitemap", action="store_true")
args = vars(parser.parse_args())


def run_sitemap_generator_process(**kwargs):
    process = SitemapGeneratorProcess(**kwargs)
    process.start()


if __name__ == "__main__":
    if args["url"] == "":
        raise Exception("url is required")

    url = args["url"]
    domain = urlparse(url).netloc
    start_urls = [url]
    base_url = url
    basic_auth_username = ""
    basic_auth_password = ""
    ip_address = ""
    is_all_page = True if args["is_all_page"] else False

    kwargs = {
        "allowed_domains": [domain],
        "start_urls": start_urls,
        "base_url": base_url,
        "basic_auth_username": basic_auth_username,
        "basic_auth_password": basic_auth_password,
        "is_all_page": is_all_page,
        "ip_address": ip_address,
    }

    run_sitemap_generator_process(**kwargs)
