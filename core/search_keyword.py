from core.crawler_bfs import bfs_crawl
from bs4 import BeautifulSoup
import requests
import logging
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def search_string(keyword, start_url='', max_depth=0, max_width=0, timeout=0):
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
    logger.info(f"Starting search for keyword '{keyword}' from {start_url} with depth {max_depth}, width {max_width}")
    
    # Validate inputs
    if not keyword or not start_url:
        logger.error("Keyword or start URL is empty")
        return []
    
    if max_depth < 1 or max_width < 1:
        logger.error("Depth and width must be at least 1")
        return []
    
    # Run the web crawler to collect pages
    result = bfs_crawl(start_url=start_url, max_depth=max_depth, max_width=max_width, timeout=timeout)
    logger.info(f"Crawler returned {len(result)} pages to search through")
    
    filtered_results = []
    for i, entry in enumerate(result):
        url = entry['url']
        current_depth = entry['depth']
        
        logger.info(f"Searching [{i+1}/{len(result)}] {url} for keyword '{keyword}'")
        try:
            response = requests.get(url, timeout=timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            html_text = soup.get_text(separator=' ', strip=True)

            # Simple string matching (case-insensitive)
            if keyword.lower() in html_text.lower():
                logger.info(f"MATCH FOUND: {url}")
                filtered_results.append(entry)
            else:
                logger.info(f"No match in {url}")
                
        except Exception as e:
            logger.error(f"Error searching {url}: {str(e)}")
            continue
    
    logger.info(f"Search complete. Found {len(filtered_results)} pages containing '{keyword}'")
    return filtered_results

# Contoh penggunaan
if __name__ == "__main__":
    import sys
    
    # Default values
    keyword = ""
    url = ""
    depth = 0
    width = 0
    
    # Use command line arguments if provided
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    if len(sys.argv) > 2:
        url = sys.argv[2]
    if len(sys.argv) > 3:
        depth = int(sys.argv[3])
    if len(sys.argv) > 4:
        width = int(sys.argv[4])
    
    print(f"Searching for '{keyword}' starting at {url} with depth={depth}, width={width}...")
    results = search_string(keyword=keyword, start_url=url, max_depth=depth, max_width=width)
    
    print(f"\nFound {len(results)} results containing '{keyword}':")
    for i, entry in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {entry['title']}")
        print(f"URL: {entry['url']}")
        print(f"Depth: {entry['depth']}")
        if entry['parent']:
            print(f"Parent: {entry['parent']}")
        print("---------------------")