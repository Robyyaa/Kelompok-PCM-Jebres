from collections import Counter

from django.core.management.base import BaseCommand

from pcm.models import AmalUsaha, Agenda, Berita, Dokumen, PesanMasuk, Pimpinan
from pcm.models import ProfilOrganisasi, Ranting, TautanTerkait


class Command(BaseCommand):
    help = "Mengisi data awal PCM Jebres yang telah diberikan."

    def handle(self, *args, **options):
        counts = Counter()

        self.seed_profil(counts)
        self.seed_pimpinan(counts)
        self.seed_ranting(counts)
        self.seed_amal_usaha(counts)
        self.seed_tautan_terkait(counts)
        self.skip_berita_tanpa_data_lengkap(counts)

        self.stdout.write("\nRingkasan seed_pcm:")
        models = (
            ProfilOrganisasi,
            Pimpinan,
            Ranting,
            AmalUsaha,
            Berita,
            Agenda,
            Dokumen,
            PesanMasuk,
            TautanTerkait,
        )
        total_created = total_skipped = 0
        for model in models:
            key = model.__name__
            created = counts[(key, "created")]
            skipped = counts[(key, "skipped")]
            total_created += created
            total_skipped += skipped
            self.stdout.write(f"- {key}: dibuat {created}, dilewati {skipped}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Total: dibuat {total_created}, dilewati {total_skipped}."
            )
        )
        self.stdout.write(
            "Berita dilewati karena isi dan tanggal terbit belum diberikan. "
            "Agenda, Dokumen, dan PesanMasuk tidak diisi karena tidak ada data "
            "awal untuk model tersebut."
        )

    @staticmethod
    def record_result(counts, model, created):
        counts[(model.__name__, "created" if created else "skipped")] += 1

    def seed_profil(self, counts):
        defaults = {
            "nama": "Pimpinan Cabang Muhammadiyah Jebres",
            "nama_singkat": "PCM Jebres",
            "alamat_sekretariat": (
                "Komplek Islamic Center Muhammadiyah Jebres, Jln. Tentara Pelajar "
                "No. 1 Kandangsapi Jebres, Surakarta."
            ),
            "sejarah": (
                "Resmi dikukuhkan oleh PWM Jawa Tengah pada 18 April 1963 atau "
                "23 Dzulqoidah 1382, saat itu bernama Muhammadiyah Grub Solo Timur."
            ),
            "visi": (
                "Menjadikan Muhammadiyah sebagai Organisasi Islam yang diandalkan, "
                "Memperbanyak manfaat bagi Umat Islam khususnya. Dan Masyarakat "
                "Jebres Pada umumnya."
            ),
            "misi": (
                "Belajar, berfikir, dan beramal untuk menjadi kader-kader muhammadiyah "
                "dan kader-kader bangsa berdasarkan kaidah Islam."
            ),
            "tentang": (
                "Pimpinan Cabang Muhammadiyah Jebres merupakan organisasi Muhammadiyah "
                "di wilayah Jebres, Surakarta. PCM Jebres dikukuhkan oleh PWM Jawa "
                "Tengah pada 18 April 1963 (23 Dzulqoidah 1382), ketika bernama "
                "Muhammadiyah Grub Solo Timur."
            ),
        }
        if ProfilOrganisasi.objects.exists():
            self.record_result(counts, ProfilOrganisasi, created=False)
            return

        _, created = ProfilOrganisasi.objects.get_or_create(pk=1, defaults=defaults)
        self.record_result(counts, ProfilOrganisasi, created)

    def seed_pimpinan(self, counts):
        data = (
            ("Ketua", "H. Bambang Condro Haryadi, S.Pd."),
            ("Wakil Ketua", "Prof. DR. H. Heri Sawiji, M.Pd"),
            ("Sekretaris", "Drs. Joko Hariyanto"),
            ("Wakil Sekretaris", "Prof. DR. H. Muhammad Sholahuddin, SE. Ph.D."),
            ("Bendahara", "Teguh Wahyudi, S.Sos"),
            ("Wakil Bendahara", "Sri Mulyono, M.Si."),
            ("Ketua Majelis Tarjih", "Drs. H. Suraji Abdullah, M.Pd"),
            ("Ketua Majelis Tabligh", "Sri Mulyana, S.Pd."),
            ("Ketua Majelis Kader", "Romansyah"),
            ("Ketua Majelis Kesehatan & Sosial", "Afif Jauhari, SE."),
            (
                "Ketua Majelis Ekonomi, Wirausaha & Pariwisata",
                "Prof. Dr. H. Muhammad Sholahuddin, SE.Ph.D",
            ),
            ("Ketua Majelis Pendidikan", "DR. Suharno"),
            ("Ketua Majelis Pustaka dan Literasi", "Agus Triyono, S.Si, M.Si."),
            ("Ketua Majelis Wakaf", "Drs. Rohadi"),
            (
                "Ketua Lembaga Pembinaan Ranting dan Kemasjidan",
                "H. Sumanto, S.Kep. M.Kes. Ners.",
            ),
            ("Ketua Lazismu", "Listyanto Eko Putra, S.Pd."),
        )

        for urutan, (jabatan, nama) in enumerate(data, start=1):
            _, created = Pimpinan.objects.get_or_create(
                jabatan=jabatan,
                defaults={"nama": nama, "urutan_tampil": urutan},
            )
            self.record_result(counts, Pimpinan, created)

    def seed_ranting(self, counts):
        names = (
            "PRM Kampung Sewu",
            "PRM Pucangsawit",
            "PRM Gandekan Tengen",
            "PRM Jagalan",
            "PRM Purwodiningratan",
            "PRM Jebres Barat",
            "PRM Jebres Timur",
            "PRM Mojosongo",
            "PRM Mojosongo Utara",
            "PRM Mojosongo Timur",
            "PRM Kepatihan Wetan",
            "PRM Kepatihan Kulon",
            "PRM Tegalharjo",
        )
        for nama in names:
            _, created = Ranting.objects.get_or_create(nama=nama)
            self.record_result(counts, Ranting, created)

    def seed_amal_usaha(self, counts):
        data = (
            ("SMP Muhammadiyah 7 Kandangsapi Jebres", AmalUsaha.Bidang.PENDIDIKAN),
            ("SD Muhammadiyah 4 Kandangsapi Jebres", AmalUsaha.Bidang.PENDIDIKAN),
            ("Rumah Toko Sewa 2 unit", AmalUsaha.Bidang.EKONOMI),
            ("Masjid Wakaf Muhammadiyah 33 unit", AmalUsaha.Bidang.SOSIAL),
        )
        for nama, bidang in data:
            _, created = AmalUsaha.objects.get_or_create(
                nama=nama,
                bidang=bidang,
            )
            self.record_result(counts, AmalUsaha, created)

    def seed_tautan_terkait(self, counts):
        links = (
            ("PDM Kota Surakarta", "https://muhammadiyahsolo.com/", 1),
            ("PWM Jawa Tengah", "https://muhammadiyahjateng.or.id/", 2),
            ("PP Muhammadiyah", "https://muhammadiyah.or.id/", 3),
        )
        for nama, url, urutan in links:
            _, created = TautanTerkait.objects.get_or_create(
                nama=nama,
                defaults={"url": url, "urutan": urutan},
            )
            self.record_result(counts, TautanTerkait, created)

    def skip_berita_tanpa_data_lengkap(self, counts):
        # Belum ada konten berita untuk di-seed; tanggal kosong kini diperbolehkan.
        counts[(Berita.__name__, "skipped")] += 5
