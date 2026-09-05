// Menegakkan kartu paket yang sedang dibaca di layar mobile.
//
// Halaman prasmanan dan menu box tidak punya nav kategori, jadi tidak ikut
// tertangani oleh menu-category-nav.js. Di desktop kartu menegak lewat :hover;
// sentuhan tidak punya hover sehingga kartu hanya menegak setelah ditekan.
document.addEventListener('DOMContentLoaded', () => {
  const kartu = Array.from(document.querySelectorAll('.prasmanan-card, .catering-card'));
  if (!kartu.length) return;

  const mq = window.matchMedia('(max-width: 991.98px)');
  const terlihat = new Set();
  let observer = null;
  let kini = null;

  const pasang = (el) => {
    if (el === kini) return;
    if (kini) kini.classList.remove('is-current');
    if (el) el.classList.add('is-current');
    kini = el;
  };

  const nyalakan = () => {
    if (observer) return;

    const topbar = document.getElementById('topbar-wrapper');
    const bandAtas = Math.max(72, topbar ? Math.round(topbar.getBoundingClientRect().height) + 16 : 0);

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) terlihat.add(entry.target);
          else terlihat.delete(entry.target);
        });

        // Kartu dengan area terbanyak di dalam band, bukan yang `top`-nya
        // terkecil - kartu yang sudah tergulung ke atas punya `top` negatif
        // sehingga selalu menang sebagai "teratas" padahal nyaris tak terlihat.
        const bandBawah = window.innerHeight * 0.55;
        let pilihan = null;
        let terluas = 0;

        terlihat.forEach((el) => {
          const r = el.getBoundingClientRect();
          const luas = Math.min(r.bottom, bandBawah) - Math.max(r.top, bandAtas);
          if (luas > terluas) { terluas = luas; pilihan = el; }
        });

        if (pilihan) pasang(pilihan);
      },
      { rootMargin: '-' + bandAtas + 'px 0px -45% 0px', threshold: 0 }
    );

    kartu.forEach((el) => observer.observe(el));
  };

  const matikan = () => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    terlihat.clear();
    pasang(null);
  };

  const sinkron = () => (mq.matches ? nyalakan() : matikan());

  mq.addEventListener('change', sinkron);
  sinkron();
});
