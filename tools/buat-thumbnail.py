"""Membuat versi kecil foto galeri: <nama>-kecil.webp dan <nama>-kecil.jpg.

Kartu galeri di beranda lebarnya sekitar 200 piksel di ponsel dan 330 piksel di
desktop, tapi sempat memuat foto ukuran penuh 1200 piksel - 327 KB hanya untuk
enam kartu kecil, dan itu memperlambat tampilnya halaman. Versi kecil ini
selebar 640 piksel (masih tajam di layar ber-resolusi tinggi) dan dipakai untuk
kartu saja; foto ukuran penuh baru diunduh ketika pengunjung mengetuk fotonya.

Jalankan dari akar repo setelah menambah foto galeri:

    pip install pillow
    python tools/buat-thumbnail.py
"""

import glob
import os

from PIL import Image

LEBAR = 640
total_penuh = 0
total_kecil = 0

for sumber in sorted(glob.glob('assets/img/posts/*.jpg')):
    if sumber.endswith('-kecil.jpg'):
        continue
    dasar = sumber[:-4]
    gambar = Image.open(sumber).convert('RGB')
    if gambar.width > LEBAR:
        tinggi = round(gambar.height * LEBAR / gambar.width)
        gambar = gambar.resize((LEBAR, tinggi), Image.LANCZOS)
    gambar.save(dasar + '-kecil.jpg', 'JPEG', quality=76, optimize=True)
    gambar.save(dasar + '-kecil.webp', 'WEBP', quality=68, method=6)

    penuh = os.path.getsize(dasar + '.webp') if os.path.exists(dasar + '.webp') else 0
    kecil = os.path.getsize(dasar + '-kecil.webp')
    total_penuh += penuh
    total_kecil += kecil
    print('%-46s %4d KB -> %3d KB' % (dasar + '-kecil.webp', penuh // 1024, kecil // 1024))

print('total webp %d KB -> %d KB' % (total_penuh // 1024, total_kecil // 1024))
