"""Membuat ulang assets/fontawesome-ringkas.css beserta font subsetnya.

Jalankan dari akar repo bila menambah ikon baru di template:

    pip install fonttools brotli
    curl -sL -o fa.css https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7/css/all.min.css
    curl -sL -o fa-solid-900.woff2 https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7/webfonts/fa-solid-900.woff2
    curl -sL -o fa-regular-400.woff2 https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7/webfonts/fa-regular-400.woff2
    cp tools/fontawesome-ringkas-head.css fa_head.css
    python tools/buat-fontawesome-ringkas.py <folder berisi keempat berkas di atas>

Skrip memindai semua kelas "fas fa-..." di template situs dan theme, lalu
memotong font Font Awesome hanya untuk ikon itu. Ikon yang dipakai lewat cara
lain (misalnya disusun dari potongan string di JavaScript) tidak akan terdeteksi.
"""

import os, re, glob, subprocess, sys
bs = chr(92)
S = sys.argv[1]
T = r"C:/Ruby34-x64/lib/ruby/gems/3.4.0/gems/jekyll-theme-chirpy-7.6.0"

srcs = []
for base in ['_layouts', '_includes', '_data', '_tabs', '_posts', 'assets']:
    srcs += [p for p in glob.glob(base + '/**/*', recursive=True)
             if os.path.isfile(p) and p.rsplit('.', 1)[-1] in ('html', 'js', 'yml', 'md')]
for base in [T + '/_includes', T + '/_layouts', T + '/assets/js/dist']:
    srcs += [p for p in glob.glob(base + '/**/*', recursive=True) if os.path.isfile(p)]

pat = re.compile(r'\bfa([srb])\s+fa-([a-z0-9-]+)')
skip = {'fw', 'li', 'spin', 'lg', 'xs', 'sm', 'stack'}
used = {}
for p in srcs:
    try:
        t = open(p, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for style, name in pat.findall(t):
        if name in skip:
            continue
        used.setdefault(name, set()).add(style)

css = open(os.path.join(S, 'fa.css'), encoding='utf-8').read()
# FA v7 menulis alias dalam satu aturan: .fa-house,.fa-home{--fa:"015"}
pola = r"((?:[.]fa-[a-z0-9-]+,)*[.]fa-[a-z0-9-]+)[{]--fa:" + chr(34) + bs + bs + r"([0-9a-f]+)" + chr(34) + r"[}]"
cp = {}
for grup, kode in re.findall(pola, css):
    for nama in re.findall(r"[.]fa-([a-z0-9-]+)", grup):
        cp[nama] = kode

# Beberapa ikon ASCII ditulis sebagai karakter, bukan kode heks: .fa-plus{--fa:"\+"}
pola_ascii = r"((?:[.]fa-[a-z0-9-]+,)*[.]fa-[a-z0-9-]+)[{]--fa:" + chr(34) + bs + bs + r"([^0-9a-f" + chr(34) + r"])" + chr(34) + r"[}]"
for grup, karakter in re.findall(pola_ascii, css):
    for nama in re.findall(r"[.]fa-([a-z0-9-]+)", grup):
        cp[nama] = "%04x" % ord(karakter)
missing = sorted(n for n in used if n not in cp)
print('ikon dipakai:', len(used), '| tidak ketemu:', missing)

solid = sorted({cp[n] for n, st in used.items() if n in cp and ('s' in st or 'b' in st)})
regular = sorted({cp[n] for n, st in used.items() if n in cp and 'r' in st})
print('glyph solid:', len(solid), 'regular:', len(regular))

os.makedirs('assets/fonts', exist_ok=True)
def subset(src, dst, codes):
    subprocess.run([sys.executable, '-m', 'fontTools.subset', os.path.join(S, src), '--output-file=' + dst,
                    '--unicodes=' + ','.join('U+' + c.upper() for c in codes),
                    '--flavor=woff2', '--layout-features=', '--no-hinting',
                    '--desubroutinize'], check=True)
subset('fa-solid-900.woff2', 'assets/fonts/fa-solid-ringkas.woff2', solid)
subset('fa-regular-400.woff2', 'assets/fonts/fa-regular-ringkas.woff2', regular)

rules = []
for n, st in sorted(used.items()):
    if n in cp:
        rules.append('.fa-%s::before { content: "%s%s"; }' % (n, bs, cp[n]))

head = open(os.path.join(S, 'fa_head.css'), encoding='utf-8').read()
open('assets/fontawesome-ringkas.css', 'w', encoding='utf-8', newline='\n').write(head + '\n'.join(rules) + '\n')
for f in ['assets/fonts/fa-solid-ringkas.woff2', 'assets/fonts/fa-regular-ringkas.woff2',
          'assets/fontawesome-ringkas.css']:
    print(f, os.path.getsize(f))
