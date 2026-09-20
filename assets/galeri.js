/*
 * Foto galeri beranda yang bisa diperbesar.
 *
 * Ditulis sendiri, bukan memakai pustaka dari luar (mis. GLightbox), supaya
 * tidak menambah unduhan pihak ketiga yang baru saja dihapus demi skor
 * kecepatan mobile.
 *
 * Catatan: komentar di berkas ini bebas gaya karena berkas .js terpisah.
 * Komentar // hanya berbahaya di dalam <script> pada halaman, sebab layout
 * "compress" theme memampatkan halaman jadi satu baris.
 */
(function () {
  var kartu = Array.prototype.slice.call(document.querySelectorAll('.galeri-kartu'));
  if (!kartu.length) return;

  var tampil = null;
  var gambar = null;
  var judul = null;
  var teks = null;
  var posisi = null;
  var pemicu = null;
  var indeks = 0;

  function buat() {
    tampil = document.createElement('div');
    tampil.className = 'galeri-tampil';
    tampil.setAttribute('role', 'dialog');
    tampil.setAttribute('aria-modal', 'true');
    tampil.setAttribute('aria-label', 'Foto suasana RM. APAYAA');
    tampil.hidden = true;
    tampil.innerHTML =
      '<button type="button" class="galeri-tampil-tutup" aria-label="Tutup foto">' +
      '<i class="fas fa-xmark" aria-hidden="true"></i></button>' +
      '<img alt="">' +
      '<div class="galeri-tampil-teks"><strong></strong><span></span></div>' +
      '<div class="galeri-tampil-nav">' +
      '<button type="button" data-arah="-1" aria-label="Foto sebelumnya">' +
      '<i class="fas fa-angle-left" aria-hidden="true"></i></button>' +
      '<span></span>' +
      '<button type="button" data-arah="1" aria-label="Foto berikutnya">' +
      '<i class="fas fa-angle-right" aria-hidden="true"></i></button>' +
      '</div>';
    document.body.appendChild(tampil);

    gambar = tampil.querySelector('img');
    judul = tampil.querySelector('.galeri-tampil-teks strong');
    teks = tampil.querySelector('.galeri-tampil-teks span');
    posisi = tampil.querySelector('.galeri-tampil-nav span');

    tampil.querySelector('.galeri-tampil-tutup').addEventListener('click', tutup);
    tampil.addEventListener('click', function (e) {
      /* Klik pada latar gelap menutup; klik pada foto atau tombol tidak. */
      if (e.target === tampil) tutup();
    });
    Array.prototype.forEach.call(tampil.querySelectorAll('[data-arah]'), function (b) {
      b.addEventListener('click', function () {
        geser(Number(b.getAttribute('data-arah')));
      });
    });
  }

  function isi(i) {
    var el = kartu[i];
    indeks = i;
    gambar.src = el.getAttribute('data-galeri-webp') || el.getAttribute('data-galeri-gambar');
    gambar.alt = el.getAttribute('data-galeri-judul') || '';
    judul.textContent = el.getAttribute('data-galeri-judul') || '';
    teks.textContent = el.getAttribute('data-galeri-teks') || '';
    posisi.textContent = (i + 1) + ' / ' + kartu.length;
  }

  function geser(arah) {
    isi((indeks + arah + kartu.length) % kartu.length);
  }

  function buka(i, tombol) {
    if (!tampil) buat();
    pemicu = tombol;
    isi(i);
    tampil.hidden = false;
    document.body.classList.add('galeri-terbuka');
    tampil.querySelector('.galeri-tampil-tutup').focus();
    document.addEventListener('keydown', tombolPapanKetik);
    /* Satu langkah riwayat ditambahkan supaya tombol Back di ponsel menutup
       foto, bukan meninggalkan halaman. */
    history.pushState({ galeri: true }, '');
  }

  function tutup(dariRiwayat) {
    if (!tampil || tampil.hidden) return;
    tampil.hidden = true;
    gambar.removeAttribute('src');
    document.body.classList.remove('galeri-terbuka');
    document.removeEventListener('keydown', tombolPapanKetik);
    if (pemicu) pemicu.focus();
    if (!dariRiwayat && history.state && history.state.galeri) history.back();
  }

  function tombolPapanKetik(e) {
    if (e.key === 'Escape') tutup();
    else if (e.key === 'ArrowRight') geser(1);
    else if (e.key === 'ArrowLeft') geser(-1);
  }

  window.addEventListener('popstate', function () {
    tutup(true);
  });

  kartu.forEach(function (el, i) {
    el.addEventListener('click', function () {
      buka(i, el);
    });
  });
})();
