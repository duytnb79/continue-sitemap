import glob
import time
import shutil
import os
import json
import sys

from base64 import urlsafe_b64encode
from urllib.parse import urlparse

file_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(file_dir)


def run_command(command, allow_errors=[], is_silent=False):
    if not is_silent:
        print("   [START] \t => " + command)
    start_time = time.time()
    status = os.system(command)
    if (status != 0) & (status not in allow_errors):
        print("   [ERROR COMMAND] \t => {}".format(status))
        sys.exit(1)
    print(
        "   [END] \t => Elapsed time: {} seconds -- {}".format(
            int(time.time() - start_time), os.path.realpath(__file__)
        )
    )  # nopep8


def get_len_list_urls(file_dir):
    list_url = []
    if os.path.isfile(file_dir):
        with open(file_dir, "r") as f_in:
            list_url = json.loads(f_in.read())
    return len(list_url) if list_url else 0


def remove_files(pattern):
    # Use glob to find all matching files
    matching_files = glob.glob(pattern)

    # Iterate over the matching files and remove them
    for file_path in matching_files:
        try:
            os.remove(file_path)
            print(f"Removed file: {file_path}")
        except Exception as e:
            print(f"Failed to remove file: {file_path} - {e}")


if __name__ == "__main__":
    url = "https://www.jpf.go.jp/"
    url = "https://www.joyobank.co.jp/index.html"
    url = "https://d2z5gcyywua7pe.cloudfront.net/"
    url = "https://quotes.toscrape.com/"
    is_new_sitemap = True
    is_all_page = True

    domain = urlparse(url).netloc

    encode_url = urlsafe_b64encode(url.encode("utf-8")).decode("utf-8").rstrip("=")
    file_dir = f"db/crawl_{encode_url}.json"
    previous_list_url = 0
    list_url = 0
    count = 1

    current_job_dir = os.path.join(root_dir, "current_job")
    stats_dir = os.path.join(root_dir, "stats")
    db_dir = os.path.join(root_dir, "db")

    if is_new_sitemap:
        while os.path.exists(current_job_dir):
            shutil.rmtree(current_job_dir)

        # Create a glob pattern to match files starting with "encode_url_" and ending with ".json"
        stats_file_pattern = os.path.join(stats_dir, f"{encode_url}_*.json")
        remove_files(stats_file_pattern)

        db_file_pattern = os.path.join(db_dir, f"crawl_{encode_url}.json")
        remove_files(stats_file_pattern)

        if os.path.isfile(file_dir):
            os.remove(file_dir)

        if not os.path.exists(stats_dir):
            os.makedirs((stats_dir))

    while list_url == 0 or list_url != previous_list_url:
        previous_list_url = get_len_list_urls(file_dir)
        print(f"\n|| ----------------[RUNNING {count} TIME]---------------- ||")
        print(f"   [PROGRESS] \t => Previous list url: {previous_list_url}")
        run_command(
            " ".join(
                [
                    sys.executable,
                    os.path.join(
                        root_dir,
                        "./run.py",
                    ),
                    f"--url {url}" if url is not None else None,
                    "--is-new-sitemap" if is_new_sitemap else "",
                    "--is-all-page" if is_all_page else "",
                ]
            )
        )
        time.sleep(5)
        is_new_sitemap = False
        list_url = get_len_list_urls(file_dir)
        print(
            f"   [PROGRESS] \t => Add list url: {list_url - previous_list_url}, init {previous_list_url}"
        )
        count += 1

        list_stats_path = glob.glob(os.path.join(stats_dir, f"{encode_url}_*.json"))
        list_stats_path = list(sorted(list_stats_path, key=lambda x: x, reverse=True))

        with open(list_stats_path[0], "r") as f_q:
            object_stats = json.loads(f_q.read())
            if object_stats.get("finish_reason") == "closespider_timeout":
                # Send sqs here
                print("   [NEXT] \t => Continue send SQS...")
            else:
                print("   [NEXT] \t => Finished sitemap")
                break
