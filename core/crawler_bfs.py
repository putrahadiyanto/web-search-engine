from bs4 import BeautifulSoup # library buat scraping crawler
from urllib.parse import urljoin, urlparse # buat parsing URL (jadi bisa tahu apakah url merupakan sub domain)
import requests # (biar bisa request http)
import logging # buat print timestamp
from flask import current_app # untuk Flask context (jika digunakan dalam aplikasi Flask)
from flask import has_app_context

# ini format logging yang akan digunakan (2025-05-26 15:04:03,425 INFO __main__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s') 

def bfs_crawl(start_url, max_depth=3, max_width=5, timeout=5, keyword=None):
    """ berfungsi untuk melakukan crawling pada website menggunakan algoritma BFS (Breadth-First Search).
    Args:
        start_url (str): URL awal untuk crawling.
        max_depth (int): Kedalaman maksimum untuk crawling.
        max_width (int): Lebar maksimum untuk crawling (jumlah link yang akan diambil pada setiap halaman).
        timeout (int): Timeout (detik) untuk request HTTP (default 5 detik).
        keyword (str, optional): Kata kunci yang dicari pada konten halaman. Jika None, semua halaman dikembalikan.
    Returns:
        list: Daftar hasil crawling yang berisi URL, judul halaman, kedalaman, dan parent URL, hanya yang mengandung keyword jika diberikan.
    """

    # Inisialisasi logger
    logger = logging.getLogger(__name__)

    # inisialisasi variabel
    visited = set() # untuk menyimpan URL yang sudah dikunjungi
    queue = [(start_url, 0, 1, None)]  # queue untuk BFS, menyimpan tuple (URL, depth, parent)
    results = [] # untuk menyimpan hasil crawling {'url': 'http://si.upi.edu', 'title': 'SMS UPI', 'depth': 1, 'parent': 'http://upi.edu'}

    # parsing data dari start_url
    parsed_start = urlparse(start_url) # untuk parsing URL awal
    base_domain = parsed_start.netloc # untuk mendapatkan domain dari URL awal
    base_scheme = parsed_start.scheme # untuk mendapatkan skema dari URL awal (http atau https)
    """ Contoh hasil dari parse
    ParseResult(
        scheme='http',
        netloc='upi.edu',
        path='',
        params='',
        query='',
        fragment=''
    )
    """


    logger.info(f"Starting BFS crawl from {start_url} with max depth {max_depth} and max width {max_width}")
    # Mulai BFS
    while queue:

        # Ambil URL dari queue (dihapu atau di pop) ditaro di current_url, depth, dan parent
        current_url, depth, width, parent = queue.pop(0)

        # Log informasi tentang URL yang sedang dikunjungi
        logger.info(f"Visiting: {current_url} at depth {depth} width {width} (parent: {parent})")

        # Cek apakah URL sudah pernah dikunjungi atau apakah kedalaman sudah melebihi max_depth (jika iya di skip)
        if current_url in visited:
            logger.debug(f"Already visited: {current_url}")
            continue
        if depth > max_depth:
            logger.debug(f"Max depth exceeded for: {current_url}")
            continue

        # Coba untuk mengambil anak URL (crawling) dari URL yang sudah di parse
        try:
            # ambil data dari current_url pake parse
            parsed_url = urlparse(current_url)
            """ Contoh hasil dari parse
            ParseResult(
                scheme='http',
                netloc='upi.edu',
                path='',
                params='',
                query='',
                fragment=''
            )
            """

            # cek apakah netloc (domain) dari parsed_url sama dengan base_domain (domain awal) atau apakah netloc berakhiran dengan base_domain (sub domain)
            if parsed_url.netloc != base_domain and not parsed_url.netloc.endswith('.' + base_domain):
                """
                yang not parsed_url.netloc.endswith('.' + base_domain)
                buat ngecek subdomain (kaya regex tapi dari belakang)
                """
                logger.info(f"Skipping {current_url} (outside base domain: {base_domain})")
                continue

            # Coba untuk mengambil data dari current_url
            logger.debug(f"Fetching: {current_url}")
            # request ke current_url dengan timeout yang bisa diatur dari params
            response = requests.get(current_url, timeout=timeout)

            # Cek status code dari response
            logger.debug(f"Status code for {current_url}: {response.status_code}")

            # Jika status code tidak 200 (OK), log peringatan dan lanjut ke URL berikutnya
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {current_url} (status: {response.status_code})")
                continue            # Parsing HTML dari response pake beautifulsoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # ambil judul dari halaman (jika ada) dan strip spasi
            title = soup.title.string.strip() if soup.title and soup.title.string else ''
            
            # Extract text content from the HTML with improved processing
            # 1. Remove script and style elements
            for script_or_style in soup(['script', 'style', 'meta', 'noscript', 'head', 'header', 'footer']):
                script_or_style.decompose()
                
            # 2. Get visible text content
            # - Using separator=' ' to replace all newlines/tabs with spaces
            # - strip=True to remove leading and trailing whitespace
            html_text = soup.get_text(separator=' ', strip=True)
            
            # 3. Normalize whitespace (replace multiple spaces with single space)
            import re
            html_text = re.sub(r'\s+', ' ', html_text).strip()
            
            # Only add to results if keyword is None or found in text (case-insensitive)
            if not keyword or (keyword.lower() in html_text.lower()):
                logger.info(f"Adding result: {current_url} (title: {title}, depth: {depth}, width: {width}, parent: {parent})")
                results.append({
                    'url': current_url, 
                    'title': title, 
                    'depth': depth, 
                    'width': width, 
                    'parent': parent,
                    'text': html_text  # Simpan extracted text content untuk pencarian
                })

            # Update CRAWL_PROGRESS if running in Flask context
            try:
                # Only update Flask app context if inside an application context
                if has_app_context():
                    current_app.config['CRAWL_PROGRESS'] = {
                        'current_depth': depth,
                        'current_width': width,
                        'max_depth': max_depth,
                        'max_width': max_width,
                        'current_url': current_url,
                        'total_visited': len(visited) + 1,
                        'matched_count': len(results)
                    }
            except Exception as e:
                logger.debug(f"Could not update CRAWL_PROGRESS: {e}")

            # Tambahkan current_url ke visited
            visited.add(current_url)

            # Jika kedalaman belum mencapai max_depth, ambil link dari halaman tersebut
            if depth < max_depth:

                # Ambil link dari halaman tersebut dan ambil href dari tag <a>
                links = [urljoin(current_url, a.get('href')) for a in soup.find_all('a', href=True)]    
                """
                Before 
                current = si.upi.edu
                <a href="http://si.upi.edu">SI UPI</a>
                <a href="/about">About</a>
                <a href="contact.html">Contact</a>
                <a href="http://google.com">Google</a>
                Contoh hasil dari links:
                [
                    "http://si.upi.edu",        
                    "http://upi.edu/about",      
                    "http://upi.edu/contact.html", 
                    "http://google.com"   
                ]
                """

                # Log jumlah link yang ditemukan
                logger.debug(f"Found {len(links)} links on {current_url}")

                # Filter link yang sesuai dengan base_domain dan belum pernah dikunjungi
                next_links = []
                # next_width = []

                # ambil link yang sesuai dengan base_domain (domain awal) atau sub domain, dan belum pernah dikunjungi
                for link in links:
                    parsed_link = urlparse(link)
                    # Cek domain dan apakah link sudah pernah dikunjungi atau sudah ada di queue
                    # Cek apakah link sudah ada di queue (hanya ambil url dari queue)
                    queue_urls = set(item[0] for item in queue)
                    if (
                        (parsed_link.netloc == base_domain or parsed_link.netloc.endswith('.' + base_domain))
                        and link not in visited
                        and link not in queue_urls
                    ):
                        next_links.append(link)
                    if len(next_links) >= max_width:
                        break

                # Log jumlah link yang akan ditambahkan ke queue
                logger.info(f"Selected {len(next_links)} new links at depth {depth+1} from {current_url}")
                logger.info(f"Expanded links from {current_url}: {next_links}")

                # Tambahkan link yang sesuai ke queue untuk diproses di depth berikutnya
                for idx, link in enumerate(next_links):
                    current_width = idx + 1  # Urutan link pada level ini (1, 2, 3, ...)
                    logger.debug(f"Queueing link: {link} (parent: {current_url}, next depth: {depth+1}, width: {current_width})")
                    queue.append((link, depth + 1, current_width, current_url))  # Pass current_url as parent

        # Jika terjadi error saat mengambil data dari current_url, log error dan lanjut ke URL berikutnya
        except Exception as e:
            logger.error(f"Error visiting {current_url}: {e}")
            continue
    logger.info(f"Crawling finished. Total pages visited: {len(visited)}. Total results: {len(results)}.")
    return results

# Only run this code if the file is executed directly
if __name__ == "__main__":
    import sys
    keyword = None
    url = 'http://upi.edu'
    depth = 3
    width = 3
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    if len(sys.argv) > 2:
        url = sys.argv[2]
    if len(sys.argv) > 3:
        depth = int(sys.argv[3])
    if len(sys.argv) > 4:
        width = int(sys.argv[4])
    result = bfs_crawl(start_url=url, max_depth=depth, max_width=width, keyword=keyword)
    print("\nCrawl Results:")
    print("=" * 60)
    for entry in result:
        print(f"URL    : {entry['url']}")
        print(f"Title  : {entry['title']}")
        print(f"Depth  : {entry['depth']}")
        print(f"Width  : {entry['width']}")
        print(f"Parent : {entry['parent']}")
        # Print first 150 characters of extracted text content as a preview
        text_preview = entry['text'][:150] + "..." if len(entry['text']) > 150 else entry['text']
        print(f"TEXT   : {text_preview}")
        print("-" * 60)

