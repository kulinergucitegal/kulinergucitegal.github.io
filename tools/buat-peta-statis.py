"""Membuat gambar peta statis assets/img/peta/peta-rm-apayaa.(webp|jpg).

Gambar ini menggantikan peta Google yang sebelumnya disematkan langsung di
beranda dan halaman maps. Peta sematan itu mengunduh sekitar 468 KB dan
menjalankan banyak skrip milik Google di setiap kunjungan; gambar ini sekitar
30 KB dan tidak menjalankan apa pun. Saat diketuk, pengunjung dibawa ke Google
Maps yang sebenarnya.

Petak peta diambil dari OpenStreetMap, yang mensyaratkan pencantuman sumber.
Keterangan "© OpenStreetMap" ditulis sebagai teks HTML di _includes/peta-statis.html
(bukan dicetak di gambar, karena sudut gambar ikut terpotong saat dipangkas) dan
tidak boleh dihapus. Google Static Maps tidak dipakai karena memerlukan kunci API berbayar.

Jalankan dari akar repo bila lokasi atau tampilan petanya perlu diperbarui:

    pip install pillow requests
    python tools/buat-peta-statis.py
"""

import io
import math
import os

import requests
from PIL import Image, ImageDraw, ImageFont

LAT = -7.1611379
LON = 109.1481706

# Petak dipakai pada ukuran aslinya. Sempat dicoba mengambil zoom 17 lalu
# mengecilkannya separuh demi ketajaman, tapi nama jalan dan nama desa ikut
# menyusut jadi setengah ukuran dan tidak terbaca di ponsel.
ZOOM = 16
SKALA = 1
LEBAR = 1024   # ukuran akhir sesudah dikecilkan
TINGGI = 680
NAMA = 'RM. APAYAA'
TUJUAN = 'assets/img/peta/peta-rm-apayaa'


def posisi_petak(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    lat_rad = math.radians(lat)
    y = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    return x, y


# Sumber petak peta. 'osm' adalah gaya standar OpenStreetMap (bebas dipakai,
# wajib mencantumkan sumber). 'carto' adalah gaya Voyager dari CARTO yang
# warnanya lebih mirip Google Maps; pemakaiannya mensyaratkan pencantuman
# "© OpenStreetMap contributors © CARTO".
SUMBER = os.environ.get('SUMBER_PETA', 'osm')
ALAMAT_PETAK = {
    'osm': 'https://tile.openstreetmap.org/%d/%d/%d.png',
    'carto': 'https://basemaps.cartocdn.com/rastertiles/voyager/%d/%d/%d.png',
}


def unduh_petak(z, x, y):
    url = ALAMAT_PETAK[SUMBER] % (z, x, y)
    r = requests.get(url, headers={'User-Agent': 'kulinergucitegal.com peta statis'}, timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert('RGB')


def huruf(ukuran):
    for nama in ('segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(nama, ukuran)
        except OSError:
            continue
    return ImageFont.load_default()


def penanda(gambar, px, py):
    """Penanda tetes air merah: ujung runcingnya tepat di titik restoran."""
    merah = (219, 68, 55)
    r = 17
    pusat_y = py - 30

    bayangan = Image.new('RGBA', gambar.size, (0, 0, 0, 0))
    ImageDraw.Draw(bayangan).ellipse([px - 13, py - 5, px + 13, py + 4], fill=(0, 0, 0, 65))
    gambar.alpha_composite(bayangan)

    d = ImageDraw.Draw(gambar)
    # Badan penanda digambar putih sedikit lebih besar lebih dulu, sebagai garis
    # tepi supaya penanda tetap terlihat di atas jalan yang juga berwarna terang.
    d.polygon([(px - 13, pusat_y + 4), (px + 13, pusat_y + 4), (px, py + 2)], fill=(255, 255, 255))
    d.ellipse([px - r - 2, pusat_y - r - 2, px + r + 2, pusat_y + r + 2], fill=(255, 255, 255))
    d.polygon([(px - 10, pusat_y + 4), (px + 10, pusat_y + 4), (px, py)], fill=merah)
    d.ellipse([px - r, pusat_y - r, px + r, pusat_y + r], fill=merah)
    d.ellipse([px - 6, pusat_y - 6, px + 6, pusat_y + 6], fill=(255, 255, 255))
    return pusat_y - r


def label(gambar, px, atas_penanda, teks):
    d = ImageDraw.Draw(gambar)
    f = huruf(22)
    kotak = d.textbbox((0, 0), teks, font=f)
    lebar_teks = kotak[2] - kotak[0]
    tinggi_teks = kotak[3] - kotak[1]
    x0 = px - lebar_teks // 2 - 14
    y0 = atas_penanda - tinggi_teks - 28
    x1 = px + lebar_teks // 2 + 14
    y1 = y0 + tinggi_teks + 20
    d.rounded_rectangle([x0 + 2, y0 + 3, x1 + 2, y1 + 3], radius=10, fill=(0, 0, 0, 60))
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(255, 255, 255))
    d.text((x0 + 14, y0 + 10 - kotak[1]), teks, font=f, fill=(32, 33, 36))


def buat():
    x, y = posisi_petak(LAT, LON, ZOOM)
    lebar_sumber = LEBAR * SKALA
    tinggi_sumber = TINGGI * SKALA
    # Titik restoran ditaruh sedikit di bawah tengah supaya label dan penanda
    # di atasnya punya ruang, seperti tampilan Google Maps.
    kiri = x * 256 - lebar_sumber / 2
    atas = y * 256 - tinggi_sumber * 0.58

    kanvas = Image.new('RGB', (lebar_sumber, tinggi_sumber))
    for tx in range(int(kiri // 256), int((kiri + lebar_sumber) // 256) + 1):
        for ty in range(int(atas // 256), int((atas + tinggi_sumber) // 256) + 1):
            kanvas.paste(unduh_petak(ZOOM, tx, ty),
                         (int(tx * 256 - kiri), int(ty * 256 - atas)))

    # Penanda digambar SESUDAH gambar dikecilkan, supaya ukurannya dihitung
    # dalam piksel akhir. Kalau digambar sebelum itu, penandanya ikut menyusut
    # separuh dan jadi terlalu kecil untuk dilihat di ponsel.
    kanvas = kanvas.resize((LEBAR, TINGGI), Image.LANCZOS).convert('RGBA')
    px = int((x * 256 - kiri) / SKALA)
    py = int((y * 256 - atas) / SKALA)
    atas_penanda = penanda(kanvas, px, py)
    label(kanvas, px, atas_penanda, NAMA)
    kanvas = kanvas.convert('RGB')

    os.makedirs(os.path.dirname(TUJUAN), exist_ok=True)
    kanvas.save(TUJUAN + '.jpg', 'JPEG', quality=82, optimize=True)
    kanvas.save(TUJUAN + '.webp', 'WEBP', quality=78, method=6)
    for ext in ('.jpg', '.webp'):
        print(TUJUAN + ext, os.path.getsize(TUJUAN + ext) // 1024, 'KB', kanvas.size)


buat()
