import argparse
import concurrent.futures
import email
import re
from datetime import date
from typing import List
from urllib.parse import urlparse

import bs4 as bs
import requests
from tqdm import tqdm


pdf_regex = re.compile(r"https://.*\.pdf", flags=re.MULTILINE)


def get_pdf_url(url: str, verbose: bool=False) -> str:
    r = requests.get(url, allow_redirects=True)  # to get content after redirection
    # Since 2024 some urls redirect directly to the PDF
    if r and "pdf" in r.headers.get("Content-Type", ""):
        if verbose:
            print(f"Direct: {url} => {r.url}")
        return r
    pdf_url_match = pdf_regex.search(r.text)
    if not pdf_url_match:
        print("Pattern not found in", r.url)
        return ""
    if verbose:
        print(f"{url} => {pdf_url_match[0]}")
    return pdf_url_match[0]


def download_pdf(url: str, year: int, month: int,
                 verbose: bool=False, dry_run: bool=False) -> None:
    if not url:
        return None

    r = get_pdf_url(url, verbose)
    content = getattr(r, "content", None) # If it was just a URL, no content
    try:
        # If we got a response object, it should have all already
        pdf_url = r.url
    except AttributeError:
        # No -- what we got is just a URL
        pdf_url = r
    
    parsed_url = urlparse(pdf_url)
    path_list = parsed_url.path.split("/")
    # year, month = path_list[-3], path_list[-2]
    filename = f"lobby99_receipts_{year}_{month:02}.pdf"
    if verbose:
        disclaimer = (
            "(not really saving)" if dry_run and content else
            "(not really downloading)" if dry_run else
            ""
        )
        action = "Saving" if content else "Downloading"
        print(f"{action} {pdf_url} into {filename} {disclaimer}")
    if dry_run:
        return
    if not content:
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
    parser.add_argument("-v", "--verbose", action="store_true",
                        default=False, help="print more details")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        default=False, help="don't really download")
    parser.add_argument("-y", "--year", type=int,
                        default=0, help="year (for file names; default last year)")
    args = parser.parse_args()
    urls = get_urls_list(args.filename)

    year = args.year or date.today().year - 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        with tqdm(total=len(urls)) as pbar:
            future_to_url = {
                executor.submit(
                    download_pdf, url, year, month, args.verbose, args.dry_run
                ): url
                for month, url in enumerate(urls, start=1)
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as e:
                    print(f"{url} generated an exception: {e}")
                finally:
                    pbar.update(1)
