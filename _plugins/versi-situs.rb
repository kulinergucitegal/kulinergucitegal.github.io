# Penanda versi yang tampil di halaman menu.
#
# Pelanggan kadang mengirim tangkapan layar menu yang ternyata versi lama. Tanpa
# penanda, tidak ada cara memastikan dari gambar saja apakah harganya masih
# berlaku. Plugin ini mengambil hash pendek dan tanggal commit terakhir, lalu
# menaruhnya di site.versi_situs untuk dirender include menu-versi.html.
#
# Diambil dari HEAD, bukan dari berkas tertentu, karena CI melakukan checkout
# dangkal (fetch-depth 1) sehingga riwayat per berkas tidak tersedia. Akibatnya
# penanda berganti di setiap deploy - itu justru yang dibutuhkan: dua tangkapan
# layar dengan penanda berbeda pasti berasal dari versi yang berbeda.

require "time"

Jekyll::Hooks.register :site, :post_read do |site|
  # File::NULL bernilai "NUL" di Windows dan "/dev/null" di Linux. Menulis
  # "/dev/null" langsung membuat perintah gagal total di cmd.exe Windows.
  commit = `git rev-parse --short HEAD 2>#{File::NULL}`.strip
  next if commit.empty?

  bulan = %w[Jan Feb Mar Apr Mei Jun Jul Agu Sep Okt Nov Des]
  iso = `git log -1 --format=%cI 2>#{File::NULL}`.strip

  tanggal =
    begin
      waktu = Time.iso8601(iso)
      "#{waktu.day} #{bulan[waktu.month - 1]} #{waktu.year}"
    rescue ArgumentError
      nil
    end

  site.config["versi_situs"] = { "commit" => commit, "tanggal" => tanggal }
end
