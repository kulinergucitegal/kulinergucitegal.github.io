// Penanda kategori aktif pada nav chip halaman menu utama.
//
// Hanya aktif di layar mobile. Di desktop kartu mengalir dalam 3 kolom,
// sehingga pada satu posisi scroll selalu ada tiga kategori berbeda yang
// sama-sama terlihat - pengukuran menunjukkan ketiganya mengisi band deteksi
// dengan selisih 1px, jadi chip yang menyala praktis acak dan justru
// menyesatkan. Di desktop seluruh chip juga sudah terlihat sekaligus dalam dua
// baris dan nav tidak pernah hilang, jadi tidak ada masalah "saya di mana"
// yang perlu dipecahkan.
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.menu-category-nav');
  if (!nav) return;

  const shell = nav.closest('.menu-category-nav-shell');
  const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
  if (!links.length) return;

  const byId = new Map();
  const sections = [];

  links.forEach((link) => {
    const id = decodeURIComponent(link.getAttribute('href').slice(1));
    const section = document.getElementById(id);
    if (!section) return;
    byId.set(section, link);
    sections.push(section);
  });

  if (!sections.length) return;

  const mq = window.matchMedia('(max-width: 991.98px)');
  let current = null;
  let observer = null;
  let ditahanSampai = 0;
  const terlihat = new Set();

  const setActive = (link) => {
    if (link === current) return;
    if (current) current.classList.remove('is-active');
    link.classList.add('is-active');
    current = link;

    // Geser nav agar chip aktif tetap terlihat, hanya bila nav memang bisa
    // digeser (di desktop chip membungkus, tidak menggeser).
    if (nav.scrollWidth > nav.clientWidth + 1) {
      const navBox = nav.getBoundingClientRect();
      const linkBox = link.getBoundingClientRect();
      if (linkBox.left < navBox.left || linkBox.right > navBox.right) {
        nav.scrollTo({
          left: nav.scrollLeft + (linkBox.left - navBox.left) - navBox.width / 2 + linkBox.width / 2,
          behavior: 'smooth'
        });
      }
    }
  };

  // Tanda bahwa masih ada chip di luar layar.
  const updateFades = () => {
    if (!shell) return;
    const max = nav.scrollWidth - nav.clientWidth;
    shell.classList.toggle('can-scroll-left', nav.scrollLeft > 4);
    shell.classList.toggle('can-scroll-right', max > 4 && nav.scrollLeft < max - 4);
  };

  nav.addEventListener('scroll', updateFades, { passive: true });
  window.addEventListener('resize', updateFades);
  updateFades();

  links.forEach((link) => {
    link.addEventListener('click', () => {
      if (!mq.matches) return;
      // Tandai seketika, lalu tahan observer sebentar supaya pilihan pengunjung
      // tidak tertimpa selagi halaman masih berpindah posisi.
      ditahanSampai = Date.now() + 700;
      setActive(link);
    });
  });

  const hitungBandAtas = () => {
    const topbar = document.getElementById('topbar-wrapper');
    const topbarH = topbar ? Math.round(topbar.getBoundingClientRect().height) : 0;
    // Tinggi nav hanya perlu dihindari kalau nav memang menempel; kalau tidak,
    // band ikut terdorong turun tanpa alasan dan jadi terlalu sempit.
    const menempel = shell && getComputedStyle(shell).position === 'sticky';
    const navH = menempel ? Math.round(shell.getBoundingClientRect().height) : 0;
    return Math.max(96, topbarH + navH + 8);
  };

  const nyalakan = () => {
    if (observer) return;
    const bandAtas = hitungBandAtas();

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) terlihat.add(entry.target);
          else terlihat.delete(entry.target);
        });

        // Yang dipilih adalah kartu dengan area terbanyak di dalam band, bukan
        // yang `top`-nya paling kecil. Kartu yang sudah tergulung ke atas punya
        // `top` negatif sehingga selalu menang sebagai "teratas", padahal yang
        // tersisa di layar cuma beberapa piksel di tepi band.
        const bandBawah = window.innerHeight * 0.30;
        let pilihan = null;
        let terluas = 0;

        terlihat.forEach((el) => {
          const r = el.getBoundingClientRect();
          const luas = Math.min(r.bottom, bandBawah) - Math.max(r.top, bandAtas);
          if (luas > terluas) { terluas = luas; pilihan = el; }
        });

        if (pilihan && Date.now() >= ditahanSampai) setActive(byId.get(pilihan));
      },
      { rootMargin: '-' + bandAtas + 'px 0px -70% 0px', threshold: 0 }
    );

    sections.forEach((section) => observer.observe(section));
  };

  const matikan = () => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    terlihat.clear();
    if (current) {
      current.classList.remove('is-active');
      current = null;
    }
  };

  const sinkron = () => (mq.matches ? nyalakan() : matikan());

  mq.addEventListener('change', sinkron);
  sinkron();
});
