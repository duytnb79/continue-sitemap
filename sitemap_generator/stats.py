from datetime import datetime
from scrapy.statscollectors import StatsCollector
from scrapy.utils.serialize import ScrapyJSONEncoder
from base64 import urlsafe_b64encode
import os

file_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(file_dir)


class MyStatsCollector(StatsCollector):
    def _persist_stats(self, stats, spider):
        encoder = ScrapyJSONEncoder()
        _now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        encode_url = (
            urlsafe_b64encode(spider.base_url.encode("utf-8"))
            .decode("utf-8")
            .rstrip("=")
        )

        stat_file_dir = os.path.join(root_dir, "..", f"stats/{encode_url}_{_now}.json")
        with open(stat_file_dir, "w") as f:
            data = encoder.encode(stats)
            f.write(data)
