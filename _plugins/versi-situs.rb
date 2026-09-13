# Penanda versi yang tampil di header situs, formatnya "v1309 646b".
#
# Pelanggan kadang mengirim tangkapan layar menu yang ternyata versi lama. Tanpa
# penanda, tidak ada cara memastikan dari gambar saja apakah harganya masih
# berlaku. Plugin ini menaruh penanda di site.versi_situs untuk dirender include
# versi-situs.html di topbar (mobile) dan sidebar (desktop).
#
# - v1309: tanggal dan bulan saat situs dibangun, dalam WIB. Build di CI berjalan
#   tepat setelah push, jadi ini tanggal push terakhir. Sengaja tanpa pemisah
#   dan tahun supaya tidak langsung terbaca sebagai tanggal oleh pelanggan.
#   Dipakai waktu build, bukan tanggal commit, karena commit bisa dibuat
#   beberapa hari sebelum di-push.
# - 646b: 4 karakter awal hash HEAD, pembeda kalau sehari ada beberapa kali push.
#   Cukup 4 karakter karena v1309 sudah membedakan harinya.
#   Diambil dari HEAD, bukan dari berkas tertentu, karena CI melakukan checkout
#   dangkal (fetch-depth 1) sehingga riwayat per berkas tidak tersedia.

Jekyll::Hooks.register :site, :post_read do |site|
  # File::NULL bernilai "NUL" di Windows dan "/dev/null" di Linux. Menulis
  # "/dev/null" langsung membuat perintah gagal total di cmd.exe Windows.
  commit = `git rev-parse HEAD 2>#{File::NULL}`.strip[0, 4].to_s
  next if commit.empty?

  # Runner CI memakai UTC; tanpa konversi, push setelah 17.00 WIB tercatat
  # sebagai tanggal kemarin.
  tanggal = Time.now.getlocal("+07:00").strftime("v%d%m")

  site.config["versi_situs"] = { "commit" => commit, "tanggal" => tanggal }
end
