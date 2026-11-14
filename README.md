# Website PCM Jebres

Website resmi Pimpinan Cabang Muhammadiyah (PCM) Jebres yang dikembangkan menggunakan Django. Website ini menyediakan informasi organisasi, pimpinan, ranting, amal usaha, berita, agenda, dokumen, dan layanan pesan masyarakat.

## Anggota Kelompok

| No. | Nama | NIM |
|---|---|---|
| 1 | Robby Arroyan Nur Hakim | L200240012 |
| 2 | Bintang Abidzar Alghifari | L200240059 |
| 3 | Rayhan Faza Darmawan | L200230032 |
| 4 | Holizah Hanufi | L200240020 |
| 5 | Afif Fajri Fauzi Fahma | L200240068 |

## Tentang Proyek

PCM Jebres merupakan salah satu Pimpinan Cabang Muhammadiyah di Kota Surakarta. Website ini dibuat sebagai media informasi digital untuk memudahkan masyarakat dalam memperoleh informasi mengenai profil organisasi, struktur pimpinan, ranting, serta amal usaha Muhammadiyah di wilayah Jebres.

## Fitur Website

- **Beranda** – Menampilkan informasi utama PCM Jebres.
- **Profil** – Informasi sejarah, visi, dan misi organisasi.
- **Pimpinan** – Menampilkan susunan pimpinan PCM Jebres.
- **Ranting** – Menampilkan daftar ranting Muhammadiyah.
- **Amal Usaha** – Informasi amal usaha yang dikelola.
- **Berita** – Menampilkan berita dan informasi kegiatan.
- **Agenda** – Informasi agenda kegiatan organisasi.
- **Unduhan** – Menyediakan dokumen yang dapat diunduh.
- **Kontak** – Formulir pesan untuk masyarakat.
- **Admin Dashboard** – Pengelolaan konten website melalui Django Admin.

## Teknologi yang Digunakan

- Python
- Django 6
- Django Templates
- HTML, CSS, dan JavaScript
- SQLite untuk pengembangan lokal
- PostgreSQL untuk lingkungan produksi
- UV untuk manajemen dependensi Python
- Docker dan Docker Compose
- Gunicorn
- WhiteNoise

## Instalasi dan Menjalankan Proyek

### 1. Clone Repository

```bash
git clone https://github.com/Robyyaa/Kelompok-PCM-Jebres.git
cd Kelompok-PCM-Jebres
```

### 2. Siapkan Environment

Pastikan Python dan UV sudah terpasang.

```bash
uv sync
```

### 3. Konfigurasi Environment

Salin file `.env.example` menjadi `.env`, kemudian sesuaikan konfigurasi yang diperlukan.

### 4. Migrasi Database

```bash
uv run python manage.py migrate
```

### 5. Isi Data Awal

```bash
uv run python manage.py seed_pcm
```

### 6. Buat Akun Admin

```bash
uv run python manage.py createsuperuser
```

### 7. Jalankan Server

```bash
uv run python manage.py runserver
```

Website dapat diakses melalui:

```text
http://127.0.0.1:8000/
```

## Menjalankan dengan Docker

Pastikan Docker Desktop sudah berjalan, kemudian jalankan:

```bash
docker compose up --build -d
```

Untuk menjalankan pengisian data awal:

```bash
docker compose exec web python manage.py seed_pcm
```

Website dapat diakses melalui:

```text
http://localhost:8000/
```

## Pengujian

Untuk menjalankan pengujian aplikasi:

```bash
uv run python manage.py test
```

## Pengelolaan Admin

Halaman administrasi Django dapat diakses melalui:

```text
http://127.0.0.1:8000/admin/
```

Gunakan akun administrator yang telah dibuat melalui perintah `createsuperuser`.

## Informasi Organisasi

**Pimpinan Cabang Muhammadiyah Jebres**

Alamat: Komplek Islamic Center Muhammadiyah Jebres, Jl. Tentara Pelajar No. 1, Kandangsapi, Jebres, Surakarta.

## Referensi Tautan

- [Muhammadiyah Kota Surakarta](https://muhammadiyahsolo.com/)
- [Pimpinan Wilayah Muhammadiyah Jawa Tengah](https://muhammadiyahjateng.or.id/)
- [Pimpinan Pusat Muhammadiyah](https://muhammadiyah.or.id/)

---

**Dikembangkan sebagai proyek tugas kelompok Teknik Informatika.**
