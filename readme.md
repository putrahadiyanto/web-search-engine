# Web Search Engine (Pencarian Web dengan BFS)

Aplikasi web ini melakukan crawling dan pencarian kata kunci pada hyperlink dalam sebuah website menggunakan algoritma Breadth-First Search (BFS). Hasil crawling dan pencarian akan ditampilkan secara interaktif melalui antarmuka web.

## Fitur
- Crawling website mulai dari URL yang diberikan
- Pencarian kata kunci pada seluruh halaman yang ditemukan
- Hanya menampilkan halaman yang mengandung kata kunci
- Menampilkan judul, URL, depth, parent, dan cuplikan teks
- Progress crawling dapat dipantau secara real-time

## Prasyarat
- Python 3.8+
- pip

## Instalasi
1. **(Opsional tapi disarankan) Buat virtual environment (venv):**
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/MacOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   Virtual environment (venv) akan membuat lingkungan Python terisolasi, sehingga library yang diinstall tidak mengganggu sistem utama.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi
1. Jalankan server Flask:
   ```bash
   python app.py
   ```
2. Buka browser dan akses: [http://localhost:5000](http://localhost:5000)

## Cara Menggunakan
1. Masukkan URL awal (contoh: `http://upi.edu`)
2. Masukkan kata kunci yang ingin dicari
3. Atur batas kedalaman (depth) dan lebar (width) crawling jika diperlukan
4. Klik tombol **Search**
5. Hasil pencarian akan muncul di bawah form

## Penjelasan Parameter
- **URL Awal**: Website yang akan dijadikan titik awal crawling
- **Kata Kunci**: Hanya halaman yang mengandung kata kunci ini yang akan ditampilkan
- **Depth**: Seberapa dalam crawler akan menelusuri link dari halaman awal
- **Width**: Berapa banyak link yang diambil dari setiap halaman pada setiap level

## Struktur Proyek
- `app.py` : Entry point aplikasi Flask
- `core/crawler_bfs.py` : Logika crawling dan pencarian BFS
- `templates/index.html` : Template HTML utama
- `requirements.txt` : Daftar dependensi Python

## Catatan
- Pastikan URL yang dimasukkan dapat diakses dari jaringan Anda.
- Proses crawling bisa memakan waktu tergantung pada jumlah halaman dan kecepatan jaringan.
- Untuk pengembangan, Anda bisa menyesuaikan parameter default di `app.py`.
