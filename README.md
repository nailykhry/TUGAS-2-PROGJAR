Tugas 02 Pemrograman Jaringan
----------------

Catatan: semua soal menggunakan pustaka socket biasa. Boleh menggunakan HTML parser seperti HTMLParser atau BeautifulSoup.
1. Cetaklah status code dan deskripsinya dari HTTP response header pada halaman its.ac.id
   Contoh output: 200 OK
   
2. Cetaklah versi Content-Encoding dari HTTP response header di halaman web its.ac.id
   Contoh output: gzip
   
3. Cetaklah versi HTTP dari HTTP response header pada halaman web its.ac.id
   Contoh output: HTTP/1.1
   
4. Cetaklah property charset pada Content-Type dari HTTP response header pada halaman classroom.its.ac.id
   Contoh output: utf-8
   
5. Dapatkanlah daftar menu pada halaman utama classroom.its.ac.id dengan melakukan parsing HTML 
   Contoh output: 
   Panduan Dosen
	Unduh PDF
	[Video] Panduan Membuat Video Asinkronus dengan Power Point
   Panduan Mahasiswa
	Unduh PDF
   
6. Membuat server dan klien HTTP sederhana.   

Spesifikasi server:
- Buatlah HTTP server yang menangani request dari klien. 
- Buatlah satu halaman html di sisi server.
- Buatlah direktori dataset yang berisi file-file seperti Tugas 01.
- Halaman html dan dataset inilah yang di-request oleh klien. 
- Server dapat diakses dengan klien yang umum digunakan misalnya Firefox dan Chrome.
- Port server yang digunakan server (misalnya port 8000) harus disimpan di dalam file terpisah, tidak boleh disimpan dalam source code.
- Menerapakan teknik multi-client dengan modul select DAN thread.
- Struktur direktori server:
  server
	- dataset
	- index.html	
	- server.py
	- httpserver.conf
	- 404.html

Spesifikasi klien:
- Klien bisa membuka file index.html dan menampilkan teks utama dalam html (tag-tag html sudah diparsing dan dibersihkan).
- Klien bisa mengunduh file di dalam direktori dataset.
- Klien bisa melihat daftar isi direktori dataset karena tidak ada file index.html di dalamnya. 
- Respon yang didukung oleh server adalah 200 OK dan 404 Not Found (bisa ditambahkan yang lain). 
