"""Memotong tangkapan layar Google Maps jadi gambar peta yang dipakai situs.

Sumbernya tools/peta/tangkapan-google-maps.png, yaitu tangkapan layar Google
Maps milik pemilik usaha. Skrip ini hanya memotong bagian antarmuka Google
(baris tombol di atas, tombol zoom dan Street View di kanan, tombol Lapisan di
kiri bawah) lalu menyimpannya sebagai .jpg dan .webp yang jauh lebih ringan.

PENTING: logo "Google Maps" dan baris "Data peta ©2026" di tepi bawah TIDAK
boleh ikut terpotong atau ditutupi. Google mengizinkan tangkapan layar petanya
dipakai selama keterangan itu tetap utuh. Karena itu pemotongan bawah berhenti
tepat di bawah baris tersebut, dan CSS menampilkan gambar dengan tepi bawah
selalu terlihat (object-position: center bottom di .peta-statis img).

Memperbarui peta: ambil tangkapan layar baru dengan panel kiri tertutup dan
tanpa kartu info tempat, simpan menimpa berkas sumber, lalu jalankan:

    pip install pillow
    python tools/potong-peta-google.py
"""

import os

from PIL import Image

SUMBER = 'tools/peta/tangkapan-google-maps.png'
TUJUAN = 'assets/img/peta/peta-rm-apayaa'

# Kotak potong (kiri, atas, kanan, bawah) pada tangkapan layar 1366x768.
POTONG = (110, 55, 1195, 645)
LEBAR_AKHIR = 1024


def potong():
    gambar = Image.open(SUMBER).convert('RGB').crop(POTONG)
    tinggi = round(gambar.height * LEBAR_AKHIR / gambar.width)
    gambar = gambar.resize((LEBAR_AKHIR, tinggi), Image.LANCZOS)

    os.makedirs(os.path.dirname(TUJUAN), exist_ok=True)
    gambar.save(TUJUAN + '.jpg', 'JPEG', quality=84, optimize=True)
    gambar.save(TUJUAN + '.webp', 'WEBP', quality=80, method=6)
    for ext in ('.jpg', '.webp'):
        print(TUJUAN + ext, os.path.getsize(TUJUAN + ext) // 1024, 'KB', gambar.size)


potong()
