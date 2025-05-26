from bs4 import BeautifulSoup # library buat scraping crawler
from urllib.parse import urljoin, urlparse # buat parsing URL (jadi bisa tahu apakah url merupakan sub domain)
import requests # (biar bisa request http)
import logging # buat print timestamp

# ini format logging yang akan digunakan (2025-05-26 15:04:03,425 INFO __main__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s') 

# ini BFS (parameternya adalah URL awal, max_depth, dan max_width)
def bfs_crawl(start_url, max_depth=3, max_width=5, timeout=5):
    """ berfungsi untuk melakukan crawling pada website menggunakan algoritma BFS (Breadth-First Search).
    Args:
        start_url (str): URL awal untuk crawling.
        max_depth (int): Kedalaman maksimum untuk crawling.
        max_width (int): Lebar maksimum untuk crawling (jumlah link yang akan diambil pada setiap halaman).
        timeout (int): Timeout (detik) untuk request HTTP (default 5 detik).
    Returns:
        list: Daftar hasil crawling yang berisi URL, judul halaman, kedalaman, dan parent URL.
    """

    # Inisialisasi logger
    logger = logging.getLogger(__name__)

    # inisialisasi variabel
    visited = set() # untuk menyimpan URL yang sudah dikunjungi
    queue = [(start_url, 0, None)]  # queue untuk BFS, menyimpan tuple (URL, depth, parent)
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
        current_url, depth, parent = queue.pop(0)

        # Log informasi tentang URL yang sedang dikunjungi
        logger.info(f"Visiting: {current_url} at depth {depth} (parent: {parent})")

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
            logger.debug(f"Status code for {current_url}: {response.status_code}\n")

            # Jika status code tidak 200 (OK), log peringatan dan lanjut ke URL berikutnya
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {current_url} (status: {response.status_code})\n")
                continue

            # Parsing HTML dari response pake beautifulsoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # ambil judul dari halaman (jika ada) dan strip spasi
            title = soup.title.string.strip() if soup.title and soup.title.string else ''
            
            # Log informasi tentang judul halaman
            logger.info(f"Adding result: {current_url} (title: {title}, depth: {depth}, parent: {parent})\n")
            
            # Tambahkan hasil crawling ke results
            results.append({'url': current_url, 'title': title, 'depth': depth, 'parent': parent})
            
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
                logger.debug(f"Found {len(links)} links on {current_url}\n")

                # Filter link yang sesuai dengan base_domain dan belum pernah dikunjungi
                next_links = []

                # ambil link yang sesuai dengan base_domain (domain awal) atau sub domain, dan belum pernah dikunjungi
                for link in links:
                    # parse link
                    parsed_link = urlparse(link)
                    # cek domain dari link dan subdomain, dan cek apakah link sudah pernah dikunjungi
                    if (parsed_link.netloc == base_domain or parsed_link.netloc.endswith('.' + base_domain)) and link not in visited:
                        # jika link sesuai dengan domain dan belum pernah dikunjungi, tambahkan ke next_links
                        next_links.append(link)

                    # batasi jumlah link yang akan diambil sesuai dengan max_width
                    if len(next_links) >= max_width:
                        break

                # Log jumlah link yang akan ditambahkan ke queue
                logger.info(f"Selected {len(next_links)} new links at depth {depth+1} from {current_url}\n")
                logger.info(f"Expanded links from {current_url}: {next_links}\n")

                # Tambahkan link yang sesuai ke queue untuk diproses di depth berikutnya
                for link in next_links:
                    logger.debug(f"Queueing link: {link} (parent: {current_url}, next depth: {depth+1})\n")
                    queue.append((link, depth + 1, current_url))  # Pass current_url as parent

        # Jika terjadi error saat mengambil data dari current_url, log error dan lanjut ke URL berikutnya
        except Exception as e:
            logger.error(f"Error visiting {current_url}: {e}")
            continue
    logger.info(f"Crawling finished. Total pages visited: {len(visited)}. Total results: {len(results)}.")
    return results

result = bfs_crawl(start_url='http://upi.edu', max_depth=3, max_width=3)
print("Crawl Results:")
for entry in result:
    print(entry)

