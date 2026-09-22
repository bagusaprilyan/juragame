#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator halaman statis juragame.com (about/contact/privacy/disclaimer/terms).

Jalankan: python3 make_static_pages.py
Menulis file HTML ke ./  (root repo, sejajar index.html).
"""
import os, datetime

SITE = "https://juragame.com"
NOW = datetime.datetime.now().strftime("%d %B %Y")

HEAD = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="no-referrer">
<title>{title} — Jura Game</title>
<meta name="description" content="{desc}">
<meta name="author" content="Jura Game">
<meta name="theme-color" content="#020617">
<link rel="canonical" href="{site}/{slug}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Jura Game">
<meta property="og:title" content="{title} — Jura Game">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{site}/{slug}">
<meta property="og:image" content="{site}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} — Jura Game">
<meta name="twitter:description" content="{desc}">
<link rel="icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body{{background:#020617;color:#e2e8f0;font-family:'Inter',system-ui,sans-serif;line-height:1.75}}
  .prose h2{{color:#fff;font-weight:800;font-size:1.35rem;margin:1.8rem 0 .6rem}}
  .prose h3{{color:#c7d2fe;font-weight:700;font-size:1.08rem;margin:1.3rem 0 .4rem}}
  .prose p{{margin:.7rem 0;color:#cbd5e1}}
  .prose ul{{margin:.6rem 0 .6rem 1.3rem;list-style:disc;color:#cbd5e1}}
  .prose li{{margin:.3rem 0}}
  .prose a{{color:#818cf8;text-decoration:underline}}
  .prose strong{{color:#fff}}
</style>
</head>
<body>
<header style="position:sticky;top:0;z-index:40;background:rgba(15,23,42,.85);backdrop-filter:blur(10px);border-bottom:1px solid #1e293b">
  <div style="max-width:56rem;margin:0 auto;padding:14px 16px;display:flex;justify-content:space-between;align-items:center">
    <a href="/" style="font-weight:900;color:#818cf8;font-size:1.25rem;text-decoration:none">Jura Game</a>
    <nav style="display:flex;gap:16px;font-size:.85rem">
      <a href="/" style="color:#94a3b8;text-decoration:none">Beranda</a>
      <a href="/blog/" style="color:#94a3b8;text-decoration:none">Blog</a>
      <a href="/about.html" style="color:#94a3b8;text-decoration:none">Tentang</a>
      <a href="/contact.html" style="color:#94a3b8;text-decoration:none">Kontak</a>
    </nav>
  </div>
</header>
<main style="max-width:56rem;margin:0 auto;padding:32px 16px 64px">
  <h1 style="color:#fff;font-weight:900;font-size:2rem;margin-bottom:.3rem">{h1}</h1>
  <p style="color:#64748b;font-size:.8rem;margin-bottom:1.6rem">Terakhir diperbarui: {now}</p>
  <article class="prose">
"""

FOOT = """  </article>
</main>
<footer style="border-top:1px solid #1e293b;margin-top:40px">
  <div style="max-width:56rem;margin:0 auto;padding:28px 16px;font-size:.82rem;color:#64748b">
    <div style="display:flex;flex-wrap:wrap;gap:18px;margin-bottom:14px">
      <a href="/" style="color:#94a3b8;text-decoration:none">Beranda</a>
      <a href="/blog/" style="color:#94a3b8;text-decoration:none">Blog &amp; Tips</a>
      <a href="/about.html" style="color:#94a3b8;text-decoration:none">Tentang Kami</a>
      <a href="/contact.html" style="color:#94a3b8;text-decoration:none">Kontak</a>
      <a href="/privacy.html" style="color:#94a3b8;text-decoration:none">Kebijakan Privasi</a>
      <a href="/disclaimer.html" style="color:#94a3b8;text-decoration:none">Disclaimer</a>
      <a href="/terms.html" style="color:#94a3b8;text-decoration:none">Syarat &amp; Ketentuan</a>
    </div>
    <p>© {year} Jura Game. Portal game HTML5 gratis — mainkan langsung di browser tanpa install.</p>
  </div>
</footer>
</body>
</html>
"""


def render(slug, title, desc, h1, body_html):
    return (HEAD.format(title=title, desc=desc, slug=slug, site=SITE, now=NOW, h1=h1)
            + body_html
            + FOOT.format(year=datetime.datetime.now().year))


PAGES = {}

# ─────────────────────────── ABOUT ───────────────────────────
PAGES["about.html"] = render(
    "about.html",
    "Tentang Kami",
    "Jura Game adalah portal game HTML5 gratis yang menyediakan ratusan game berkualitas untuk dimainkan langsung di browser tanpa install.",
    "Tentang Jura Game",
    """
    <p><strong>Jura Game</strong> adalah portal game HTML5 gratis yang lahir dari satu keyakinan sederhana: bermain game tidak harus rumit, mahal, atau memakan ruang penyimpanan. Kami menyediakan koleksi game kasual berkualitas yang bisa langsung dimainkan di browser — baik di HP maupun komputer — tanpa perlu mengunduh atau memasang aplikasi apa pun.</p>

    <h2>Apa yang Kami Sediakan</h2>
    <p>Kami mengumpulkan dan mengurasi game HTML5 dari berbagai penyedia resmi, lalu menyajikannya dalam satu tempat yang rapi, cepat, dan bebas gangguan. Kategori yang tersedia mencakup:</p>
    <ul>
      <li><strong>Puzzle &amp; Logika</strong> — melatih otak sekaligus mengisi waktu luang.</li>
      <li><strong>Action &amp; Arcade</strong> — permainan cepat dengan tempo tinggi.</li>
      <li><strong>Racing</strong> — balapan ringan yang lancar bahkan di perangkat sederhana.</li>
      <li><strong>Strategy</strong> — permainan taktik yang membutuhkan perencanaan.</li>
      <li><strong>RPG &amp; Petualangan</strong> — cerita ringan yang bisa ditamatkan dalam sekali duduk.</li>
    </ul>

    <h2>Misi Kami</h2>
    <p>Misi kami adalah menjadikan hiburan digital berkualitas bisa diakses siapa saja — termasuk pengguna dengan perangkat sederhana, koneksi terbatas, atau mereka yang tidak ingin menyimpan banyak aplikasi di perangkatnya. Kami percaya game yang baik adalah game yang bisa dinikmati tanpa hambatan teknis.</p>

    <h2>Bagaimana Kami Bekerja</h2>
    <p>Setiap game di Jura Game dijalankan langsung di browser Anda melalui teknologi HTML5. Artinya permainan berlangsung di perangkat Anda sendiri dan tidak memerlukan pemasangan. Kami juga secara rutin menambahkan judul baru serta menulis panduan dan tips di <a href="/blog/">blog kami</a> untuk membantu pemain menemukan game yang paling sesuai dengan selera mereka.</p>

    <h2>Konten &amp; Ulasan</h2>
    <p>Selain bermain, kami menulis artikel yang benar-benar berguna: daftar rekomendasi game berdasarkan tema, panduan untuk pemula, dan tips memilih game yang cocok untuk anak-anak. Setiap artikel kami susun dengan riset dan ditulis ulang dengan gaya kami sendiri agar memberi informasi yang jujur dan bermanfaat bagi pembaca.</p>

    <h2>Hubungi Kami</h2>
    <p>Punya pertanyaan, masukan, atau ingin bekerja sama? Kami senang mendengar dari Anda. Silakan kunjungi halaman <a href="/contact.html">Kontak</a> atau kirim surel ke <a href="mailto:halo@juragame.com"><a href="mailto:halo@juragame.com"><strong>halo@juragame.com</strong></a></a>.</p>

    <p>Terima kasih telah bermain di Jura Game. Selamat bersenang-senang! 🎮</p>
    """,
)

# ─────────────────────────── PRIVACY ───────────────────────────
PAGES["privacy.html"] = render(
    "privacy.html",
    "Kebijakan Privasi",
    "Kebijakan privasi Jura Game: bagaimana kami mengumpulkan, menggunakan, dan melindungi data pengunjung serta penggunaan cookie dan iklan pihak ketiga.",
    "Kebijakan Privasi",
    """
    <p>Privasi Anda penting bagi kami. Kebijakan Privasi ini menjelaskan bagaimana <strong>Jura Game</strong> menangani informasi saat Anda mengunjungi situs kami, serta pilihan yang Anda miliki terkait data tersebut. Dengan menggunakan situs ini, Anda menyetujui praktik yang dijelaskan di bawah.</p>

    <h2>1. Informasi yang Kami Kumpulkan</h2>
    <p>Kami dapat mengumpulkan dua jenis informasi:</p>
    <ul>
      <li><strong>Informasi non-pribadi secara otomatis:</strong> jenis perangkat, browser, sistem operasi, halaman yang dikunjungi, waktu kunjungan, dan data statistik agregat lainnya. Data ini tidak dapat mengidentifikasi Anda secara pribadi.</li>
      <li><strong>Informasi yang Anda berikan sukarela:</strong> seperti alamat surel atau isi pesan apabila Anda menghubungi kami melalui halaman Kontak.</li>
    </ul>

    <h2>2. Bagaimana Kami Menggunakan Informasi</h2>
    <ul>
      <li>Menyediakan, mengoperasikan, dan meningkatkan layanan situs.</li>
      <li>Memahami bagaimana pengunjung menggunakan situs kami agar konten lebih relevan.</li>
      <li>Menjawab pertanyaan atau permintaan yang Anda kirimkan.</li>
      <li>Menjaga keamanan dan mencegah penyalahgunaan.</li>
    </ul>

    <h2>3. Cookie dan Teknologi Serupa</h2>
    <p>Kami menggunakan cookie untuk menyimpan preferensi Anda, misalnya pilihan bahasa (Indonesia/Inggris) dan riwayat game yang terakhir dimainkan. Cookie adalah berkas kecil yang disimpan di perangkat Anda dan dapat dihapus kapan saja melalui pengaturan browser.</p>
    <p>Anda dapat menolak atau menghapus cookie melalui pengaturan browser Anda. Namun perlu diketahui, menonaktifkan cookie dapat memengaruhi sebagian fungsi situs.</p>

    <h2>4. Iklan Pihak Ketiga (Google AdSense)</h2>
    <p>Situs ini dapat menampilkan iklan melalui <strong>Google AdSense</strong> dan mitra periklanan lainnya. Penyedia iklan pihak ketiga ini dapat menggunakan cookie (termasuk cookie DoubleClick) untuk menayangkan iklan berdasarkan kunjungan Anda ke situs ini maupun situs lain di internet.</p>
    <ul>
      <li>Penggunaan cookie iklan oleh Google memungkinkan Google dan mitranya menayangkan iklan yang lebih relevan bagi Anda.</li>
      <li>Anda dapat menonaktifkan personalisasi iklan melalui <a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Pengaturan Iklan Google</a>.</li>
      <li>Informasi lebih lanjut tersedia di <a href="https://policies.google.com/technologies/ads" rel="nofollow noopener" target="_blank">Kebijakan Iklan Google</a>.</li>
    </ul>

    <h2>5. Analytics</h2>
    <p>Kami dapat menggunakan layanan analitik (seperti Google Analytics) untuk memahami lalu lintas situs secara agregat. Layanan ini dapat mencatat data seperti alamat IP, jenis perangkat, dan perilaku navigasi. Data tersebut digunakan semata-mata untuk peningkatan kualitas layanan.</p>

    <h2>6. Berbagi Informasi dengan Pihak Ketiga</h2>
    <p>Kami <strong>tidak menjual, menyewakan, atau memperdagangkan</strong> informasi pribadi Anda. Kami hanya membagikan data kepada penyedia layanan tepercaya (misalnya penyedia analitik dan periklanan) yang membantu kami mengoperasikan situs, dan mereka wajib menjaga kerahasiaan data tersebut.</p>

    <h2>7. Tautan ke Situs Lain</h2>
    <p>Situs kami memuat game dan tautan ke situs pihak ketiga. Kami tidak bertanggung jawab atas praktik privasi atau konten situs pihak ketiga tersebut. Kami menyarankan Anda membaca kebijakan privasi masing-masing situs yang Anda kunjungi.</p>

    <h2>8. Privasi Anak-anak</h2>
    <p>Situs kami tidak ditujukan untuk anak di bawah usia 13 tahun dan kami tidak dengan sengaja mengumpulkan data pribadi dari anak-anak. Jika Anda yakin seorang anak telah memberikan informasi pribadi kepada kami, silakan hubungi kami untuk menghapusnya.</p>

    <h2>9. Hak Anda</h2>
    <p>Anda berhak untuk meminta akses, koreksi, atau penghapusan data pribadi yang kami miliki tentang Anda. Untuk menggunakan hak tersebut, silakan hubungi kami melalui halaman <a href="/contact.html">Kontak</a>.</p>

    <h2>10. Perubahan Kebijakan</h2>
    <p>Kami dapat memperbarui Kebijakan Privasi ini dari waktu ke waktu. Perubahan akan ditampilkan di halaman ini dengan tanggal pembaruan terbaru. Kami menyarankan Anda meninjau halaman ini secara berkala.</p>

    <h2>11. Hubungi Kami</h2>
    <p>Jika Anda memiliki pertanyaan tentang Kebijakan Privasi ini, silakan hubungi kami di <a href="mailto:halo@juragame.com"><a href="mailto:halo@juragame.com"><strong>halo@juragame.com</strong></a></a>.</p>
    """,
)

# ─────────────────────────── DISCLAIMER ───────────────────────────
PAGES["disclaimer.html"] = render(
    "disclaimer.html",
    "Disclaimer",
    "Disclaimer Jura Game: informasi mengenai kepemilikan konten game, batasan tanggung jawab, serta penggunaan materi di situs ini.",
    "Disclaimer",
    """
    <p>Informasi dan materi di situs <strong>Jura Game</strong> (juragame.com) disediakan untuk tujuan hiburan dan informasi umum. Dengan mengakses situs ini, Anda menyetujui ketentuan dalam halaman Disclaimer ini.</p>

    <h2>1. Konten Game</h2>
    <p>Game yang ditampilkan di Jura Game disediakan oleh penyedia pihak ketiga melalui teknologi embed (iframe). Hak cipta atas setiap game sepenuhnya milik pengembang atau pemiliknya masing-masing. Jura Game tidak mengklaim kepemilikan atas game apa pun dan hanya berperan sebagai portal yang memudahkan pengguna menemukan permainan.</p>

    <h2>2. Akurasi Informasi</h2>
    <p>Kami berupaya menyajikan informasi yang akurat dan terkini, termasuk ulasan, rekomendasi, dan artikel di blog kami. Namun kami tidak menjamin bahwa semua informasi selalu lengkap, akurat, atau terbaru. Perubahan pada game pihak ketiga dapat terjadi tanpa sepengetahuan kami.</p>

    <h2>3. Batasan Tanggung Jawab</h2>
    <p>Jura Game tidak bertanggung jawab atas:</p>
    <ul>
      <li>Gangguan teknis, kehilangan data, atau kerusakan perangkat akibat penggunaan game pihak ketiga.</li>
      <li>Konten, kebijakan, atau praktik dari situs dan layanan pihak ketiga yang ditautkan.</li>
      <li>Keputusan yang diambil pengguna berdasarkan informasi di situs ini.</li>
    </ul>

    <h2>4. Tautan Eksternal</h2>
    <p>Situs ini memuat tautan ke situs eksternal. Kami tidak mengontrol dan tidak bertanggung jawab atas isi maupun ketersediaan situs tersebut. Kehadiran tautan tidak menyiratkan dukungan terhadap pandangan atau kontennya.</p>

    <h2>5. Iklan</h2>
    <p>Situs ini menampilkan iklan dari jaringan pihak ketiga, termasuk Google AdSense. Kami tidak bertanggung jawab atas isi iklan maupun produk/layanan yang diiklankan. Setiap transaksi dengan pengiklan merupakan tanggung jawab pengguna dan pengiklan terkait.</p>

    <h2>6. Penggunaan yang Wajar</h2>
    <p>Anda setuju untuk menggunakan situs ini hanya untuk tujuan yang sah dan tidak melanggar hak pihak lain. Segala bentuk penyalahgunaan, termasuk upaya merusak situs, dilarang.</p>

    <h2>7. Perubahan</h2>
    <p>Kami dapat mengubah Disclaimer ini kapan saja. Versi terbaru akan selalu ditampilkan di halaman ini.</p>

    <h2>8. Kontak</h2>
    <p>Pertanyaan mengenai Disclaimer ini dapat disampaikan ke <a href="mailto:halo@juragame.com"><a href="mailto:halo@juragame.com"><strong>halo@juragame.com</strong></a></a> atau melalui halaman <a href="/contact.html">Kontak</a>.</p>
    """,
)

# ─────────────────────────── TERMS ───────────────────────────
PAGES["terms.html"] = render(
    "terms.html",
    "Syarat & Ketentuan",
    "Syarat dan ketentuan penggunaan situs Jura Game, termasuk aturan penggunaan, hak kekayaan intelektual, dan ketentuan lainnya.",
    "Syarat &amp; Ketentuan",
    """
    <p>Selamat datang di <strong>Jura Game</strong>. Dengan mengakses dan menggunakan situs ini, Anda dianggap telah membaca, memahami, dan menyetujui Syarat &amp; Ketentuan berikut. Jika Anda tidak setuju, mohon untuk tidak menggunakan situs ini.</p>

    <h2>1. Penerimaan Ketentuan</h2>
    <p>Penggunaan situs juragame.com berarti Anda menyetujui seluruh ketentuan yang tercantum di halaman ini beserta <a href="/privacy.html">Kebijakan Privasi</a> dan <a href="/disclaimer.html">Disclaimer</a> kami.</p>

    <h2>2. Penggunaan Layanan</h2>
    <p>Jura Game menyediakan portal game HTML5 gratis. Anda setuju untuk:</p>
    <ul>
      <li>Menggunakan situs hanya untuk tujuan pribadi dan non-komersial yang sah.</li>
      <li>Tidak menyalin, menggandakan, atau mendistribusikan ulang konten situs tanpa izin.</li>
      <li>Tidak melakukan tindakan yang dapat mengganggu atau merusak situs.</li>
      <li>Tidak menggunakan alat otomatis untuk memanen konten dari situs ini.</li>
    </ul>

    <h2>3. Hak Kekayaan Intelektual</h2>
    <p>Seluruh merek, logo, dan konten asli Jura Game (termasuk artikel blog) dilindungi hak cipta dan merupakan milik kami. Game pihak ketiga tetap menjadi milik pengembang masing-masing. Anda tidak diperkenankan menggunakan materi kami tanpa izin tertulis.</p>

    <h2>4. Konten Pihak Ketiga</h2>
    <p>Situs ini menampilkan game dan konten dari pihak ketiga. Kami tidak bertanggung jawab atas kualitas, keamanan, atau legalitas konten pihak ketiga tersebut. Jika Anda menemukan konten yang melanggar hak Anda, silakan hubungi kami untuk penanganan lebih lanjut.</p>

    <h2>5. Penafian Jaminan</h2>
    <p>Situs dan layanan disediakan "sebagaimana adanya" tanpa jaminan apa pun, baik tersurat maupun tersirat. Kami tidak menjamin situs akan selalu tersedia, bebas kesalahan, atau bebas dari virus.</p>

    <h2>6. Batasan Tanggung Jawab</h2>
    <p>Sejauh diizinkan hukum, Jura Game tidak bertanggung jawab atas kerugian langsung maupun tidak langsung yang timbul dari penggunaan atau ketidakmampuan menggunakan situs ini.</p>

    <h2>7. Perubahan Layanan</h2>
    <p>Kami berhak mengubah, menangguhkan, atau menghentikan sebagian atau seluruh layanan kapan saja tanpa pemberitahuan sebelumnya.</p>

    <h2>8. Perubahan Ketentuan</h2>
    <p>Kami dapat memperbarui Syarat &amp; Ketentuan ini sewaktu-waktu. Kelanjutan penggunaan situs setelah perubahan berarti Anda menyetujui ketentuan yang diperbarui.</p>

    <h2>9. Hukum yang Berlaku</h2>
    <p>Syarat &amp; Ketentuan ini diatur oleh hukum yang berlaku di Indonesia. Segala perselisihan akan diselesaikan secara musyawarah terlebih dahulu.</p>

    <h2>10. Kontak</h2>
    <p>Untuk pertanyaan mengenai Syarat &amp; Ketentuan ini, hubungi kami di <a href="mailto:halo@juragame.com"><a href="mailto:halo@juragame.com"><strong>halo@juragame.com</strong></a></a> atau melalui halaman <a href="/contact.html">Kontak</a>.</p>
    """,
)

# ─────────────────────────── CONTACT ───────────────────────────
PAGES["contact.html"] = render(
    "contact.html",
    "Kontak",
    "Hubungi tim Jura Game untuk pertanyaan, masukan, laporan konten, atau peluang kerja sama. Kami senang mendengar dari Anda.",
    "Hubungi Kami",
    """
    <p>Kami senang mendengar dari pengunjung Jura Game. Apakah Anda punya pertanyaan, masukan, menemukan gangguan, atau ingin bekerja sama? Silakan hubungi kami melalui salah satu cara di bawah ini.</p>

    <h2>Cara Menghubungi Kami</h2>
    <ul>
      <li><strong>Surel:</strong> <a href="mailto:halo@juragame.com">halo@juragame.com</a> — untuk pertanyaan umum, masukan, dan kerja sama.</li>
      <li><strong>Laporan konten:</strong> <a href="mailto:legal@juragame.com">legal@juragame.com</a> — untuk laporan pelanggaran hak cipta atau konten tidak pantas.</li>
      <li><strong>Pengembang game:</strong> <a href="mailto:partner@juragame.com">partner@juragame.com</a> — jika Anda ingin game Anda ditampilkan di Jura Game.</li>
    </ul>

    <h2>Waktu Respons</h2>
    <p>Kami berusaha membalas setiap pesan dalam <strong>1–3 hari kerja</strong>. Untuk laporan yang menyangkut keamanan atau pelanggaran hukum, kami akan memprioritaskan penanganannya.</p>

    <h2>Yang Perlu Disertakan</h2>
    <p>Agar kami dapat membantu lebih cepat, mohon sertakan:</p>
    <ul>
      <li>Nama dan cara menghubungi Anda kembali.</li>
      <li>Penjelasan singkat mengenai pertanyaan atau masalah Anda.</li>
      <li>Tautan (URL) halaman terkait jika masalah menyangkut halaman tertentu.</li>
      <li>Tangkapan layar bila relevan.</li>
    </ul>

    <h2>Pertanyaan yang Sering Diajukan</h2>
    <h3>Apakah semua game di Jura Game gratis?</h3>
    <p>Ya. Seluruh game yang kami tampilkan dapat dimainkan secara gratis tanpa biaya tersembunyi.</p>
    <h3>Apakah saya perlu memasang aplikasi?</h3>
    <p>Tidak. Semua game berjalan langsung di browser Anda, baik di HP maupun komputer.</p>
    <h3>Bagaimana cara menampilkan game saya di Jura Game?</h3>
    <p>Silakan kirim surel ke <a href="mailto:partner@juragame.com">partner@juragame.com</a> beserta tautan embed game Anda, dan tim kami akan meninjau kelayakannya.</p>

    <h2>Media Sosial</h2>
    <p>Ikuti kami untuk pembaruan game dan artikel terbaru. Tautan media sosial kami akan segera tersedia di halaman ini.</p>

    <p>Terima kasih atas dukungan Anda terhadap Jura Game. 🎮</p>
    """,
)


def main():
    out = os.path.dirname(os.path.abspath(__file__))
    for name, content in PAGES.items():
        path = os.path.join(out, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {name:18} {len(content):>6} bytes")
    print(f"\nSelesai: {len(PAGES)} halaman statis dibuat.")


if __name__ == "__main__":
    main()
