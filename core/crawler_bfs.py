from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

def bfs_crawl(start_url, max_depth=3, max_width=5):
    logger = logging.getLogger(__name__)
    visited = set()
    queue = [(start_url, 0, None)]  # Add parent as None for the root
    results = []

    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    base_scheme = parsed_start.scheme

    while queue:
        current_url, depth, parent = queue.pop(0)
        logger.info(f"Visiting: {current_url} at depth {depth} (parent: {parent})")
        if current_url in visited:
            logger.debug(f"Already visited: {current_url}")
            continue
        if depth > max_depth:
            logger.debug(f"Max depth exceeded for: {current_url}")
            continue
        try:
            parsed_url = urlparse(current_url)
            # Only crawl if the domain matches the start_url's domain (subdomain or same domain)
            if parsed_url.netloc != base_domain and not parsed_url.netloc.endswith('.' + base_domain):
                logger.info(f"Skipping {current_url} (outside base domain: {base_domain})")
                continue
            logger.debug(f"Fetching: {current_url}")
            response = requests.get(current_url, timeout=5)
            logger.debug(f"Status code for {current_url}: {response.status_code}")
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {current_url} (status: {response.status_code})")
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else ''
            logger.info(f"Adding result: {current_url} (title: {title}, depth: {depth}, parent: {parent})")
            results.append({'url': current_url, 'title': title, 'depth': depth, 'parent': parent})
            visited.add(current_url)
            if depth < max_depth:
                links = [urljoin(current_url, a.get('href')) for a in soup.find_all('a', href=True)]
                logger.debug(f"Found {len(links)} links on {current_url}")
                # Filter out already visited and limit width
                next_links = []
                for link in links:
                    parsed_link = urlparse(link)
                    if (parsed_link.netloc == base_domain or parsed_link.netloc.endswith('.' + base_domain)) and link not in visited:
                        next_links.append(link)
                    if len(next_links) >= max_width:
                        break
                logger.info(f"Selected {len(next_links)} new links at depth {depth+1} from {current_url}")
                for link in next_links:
                    logger.debug(f"Queueing link: {link} (parent: {current_url}, next depth: {depth+1})")
                    queue.append((link, depth + 1, current_url))  # Pass current_url as parent
        except Exception as e:
            logger.error(f"Error visiting {current_url}: {e}")
            continue
    logger.info(f"Crawling finished. Total pages visited: {len(visited)}. Total results: {len(results)}.")
    return results

result = bfs_crawl(start_url='http://upi.edu', max_depth=3, max_width=3)
print("Crawl Results:")
for entry in result:
    print(entry)

