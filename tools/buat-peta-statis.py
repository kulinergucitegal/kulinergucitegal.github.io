"""Membuat gambar peta statis assets/img/peta/peta-rm-apayaa.(webp|jpg).

Gambar ini menggantikan peta Google yang sebelumnya disematkan langsung di
beranda dan halaman maps. Peta sematan itu mengunduh sekitar 468 KB dan
menjalankan banyak skrip milik Google di setiap kunjungan; gambar ini sekitar
30 KB dan tidak menjalankan apa pun. Saat diketuk, pengunjung dibawa ke Google
Maps yang sebenarnya.

Petak peta diambil dari OpenStreetMap, yang mensyaratkan pencantuman sumber.
Tulisan "© OpenStreetMap" sudah ditempelkan di sudut gambar dan tidak boleh
dihapus. Google Static Maps tidak dipakai karena memerlukan kunci API berbayar.

Jalankan dari akar repo bila lokasi atau tampilan petanya perlu diperbarui:

    pip install pillow requests
    python tools/buat-peta-statis.py
"""

import io
import math
import os

import requests
from PIL import Image, ImageDraw

LAT = -7.1611379
LON = 109.1481706
ZOOM = 15
LEBAR_PETAK = 3   # 3 x 2 petak = 768 x 512 piksel
TINGGI_PETAK = 2
TUJUAN = 'assets/img/peta/peta-rm-apayaa'


def petak(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    lat_rad = math.radians(lat)
    y = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    return x, y


def ambil():
    x, y = petak(LAT, LON, ZOOM)
    x0 = int(x) - LEBAR_PETAK // 2
    y0 = int(y) - TINGGI_PETAK // 2
    kanvas = Image.new('RGB', (256 * LEBAR_PETAK, 256 * TINGGI_PETAK))
    for dx in range(LEBAR_PETAK):
        for dy in range(TINGGI_PETAK):
            url = 'https://tile.openstreetmap.org/%d/%d/%d.png' % (ZOOM, x0 + dx, y0 + dy)
            r = requests.get(url, headers={'User-Agent': 'kulinergucitegal.com peta statis'}, timeout=30)
            r.raise_for_status()
            kanvas.paste(Image.open(io.BytesIO(r.content)).convert('RGB'), (256 * dx, 256 * dy))

    # Penanda lokasi tepat di titik restoran.
    px = int((x - x0) * 256)
    py = int((y - y0) * 256)
    gambar = ImageDraw.Draw(kanvas)
    for r, warna in ((15, (255, 255, 255)), (11, (220, 38, 38)), (4, (255, 255, 255))):
        gambar.ellipse([px - r, py - r, px + r, py + r], fill=warna)
    gambar.rectangle([0, kanvas.height - 16, 150, kanvas.height], fill=(255, 255, 255))
    gambar.text((4, kanvas.height - 13), '(c) OpenStreetMap', fill=(60, 60, 60))

    os.makedirs(os.path.dirname(TUJUAN), exist_ok=True)
    kanvas.save(TUJUAN + '.jpg', 'JPEG', quality=82, optimize=True)
    kanvas.save(TUJUAN + '.webp', 'WEBP', quality=78, method=6)
    for ext in ('.jpg', '.webp'):
        print(TUJUAN + ext, os.path.getsize(TUJUAN + ext) // 1024, 'KB', kanvas.size)


ambil()
