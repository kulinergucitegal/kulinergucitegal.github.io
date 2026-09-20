"""Membuat versi .webp berdampingan untuk setiap foto .jpg di assets/img.

Jalankan dari akar repo setelah menambah atau mengganti foto:

    pip install pillow
    python tools/buat-webp.py

Berkas .jpg aslinya tetap disimpan: dipakai sebagai gambar pratinjau saat link
dibagikan (og:image) dan sebagai cadangan untuk browser lama. Halaman memuat
.webp lewat _includes/gambar.html, yang otomatis jatuh ke .jpg bila perlu.
"""

import glob
import os

from PIL import Image

total_jpg = 0
total_webp = 0

for sumber in sorted(glob.glob('assets/img/**/*.jpg', recursive=True)):
    tujuan = sumber[:-4] + '.webp'
    gambar = Image.open(sumber).convert('RGB')
    gambar.save(tujuan, 'WEBP', quality=76, method=6)
    besar_jpg = os.path.getsize(sumber)
    besar_webp = os.path.getsize(tujuan)
    total_jpg += besar_jpg
    total_webp += besar_webp
    print('%-52s %4d KB -> %4d KB' % (tujuan, besar_jpg // 1024, besar_webp // 1024))

print('total %d KB -> %d KB' % (total_jpg // 1024, total_webp // 1024))
