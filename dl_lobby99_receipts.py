from typing import List
import requests
import re
import email
import bs4 as bs
from urllib.parse import urlparse
import argparse
import concurrent.futures
from tqdm import tqdm

pdf_regex = re.compile("https:\/\/.*\.pdf", flags=re.MULTILINE)


def get_pdf_url(url: str) -> str:
    r = requests.get(url, allow_redirects=True)  # to get content after redirection
    pdf_url_match = pdf_regex.search(r.text)
    if not pdf_url_match:
        print("Pattern not found on", r.text)

    return pdf_url_match[0]


def download_pdf(pdf_url: str) -> None:
    parsed_url = urlparse(pdf_url)
    path_list = parsed_url.path.split("/")
    year, month = path_list[-3], path_list[-2]
    r = requests.get(pdf_url)
    with open(f"lobby99_receipts_{year}_{month:02}.pdf", "wb") as writer:
        writer.write(r.content)


def get_urls_list(filename: str) -> List[str]:
    with open(filename) as email_file:
        email_message = email.message_from_file(email_file)

    sp = bs.BeautifulSoup(email_message.get_payload(), "lxml")
    pdf_urls = []
    for a in sp.find_all("a"):
        if a.has_attr("href") and "pdf" in a.text.lower():
            pdf_urls.append(a["href"])

    return pdf_urls


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lobby99 receipts downloader")
    parser.add_argument("filename", help="email file name")
    args = parser.parse_args()
    urls = get_urls_list(args.filename)
    pdf_urls = [get_pdf_url(url) for url in urls]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        with tqdm(total=len(pdf_urls)) as pbar:
            future_to_url = {
                executor.submit(download_pdf, url): url for url in pdf_urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as e:
                    print(f"{url} generated an exception: {e}")
                finally:
                    pbar.update(1)
