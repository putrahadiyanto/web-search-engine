from core.crawler_bfs import bfs_crawl
from bs4 import BeautifulSoup
import requests

def search_string(keyword, start_url='http://upi.edu', max_depth=3, max_width=3, timeout=5):
    """
    Melakukan pencarian keyword pada seluruh atribut HTML dari hasil bfs_crawl.
    Args:
        keyword (str): Kata kunci yang dicari.
        start_url (str): URL awal untuk crawling.
        max_depth (int): Kedalaman maksimum crawling.
        max_width (int): Lebar maksimum crawling.
        timeout (int): Timeout request HTTP.
    Returns:
        list: Hasil crawling yang mengandung keyword.
    """
    result = bfs_crawl(start_url=start_url, max_depth=max_depth, max_width=max_width, timeout=timeout)
    filtered_results = []
    for entry in result:
        url = entry['url']
        try:
            response = requests.get(url, timeout=timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            html_text = soup.get_text(separator=' ', strip=True)
            # Simple string matching (case-insensitive)
            if keyword.lower() in html_text.lower():
                filtered_results.append(entry)
        except Exception as e:
            continue
    return filtered_results

# Contoh penggunaan
if __name__ == "__main__":
    keyword = "beasiswa"
    results = search_string(keyword)
    print(f"Hasil pencarian untuk keyword '{keyword}':")
    for entry in results:
        print(entry)