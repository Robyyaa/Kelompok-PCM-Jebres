from datetime import timedelta
from io import StringIO
from tempfile import TemporaryDirectory

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.finders import find
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Agenda,
    AmalUsaha,
    Berita,
    Dokumen,
    PesanMasuk,
    Pimpinan,
    ProfilOrganisasi,
    Ranting,
    TautanTerkait,
)


class PublicPageTests(TestCase):
    def test_all_public_listing_pages_render_without_seed_content(self):
        routes = (
            "pcm:home",
            "pcm:profil",
            "pcm:pimpinan",
            "pcm:ranting",
            "pcm:amal_usaha",
            "pcm:berita_list",
            "pcm:agenda",
            "pcm:unduhan",
            "pcm:kontak",
        )
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)

    def test_public_listings_use_empty_states_when_content_is_missing(self):
        checks = (
            ("pcm:pimpinan", b"Data pimpinan belum tersedia."),
            ("pcm:ranting", b"Data ranting belum tersedia."),
            ("pcm:amal_usaha", b"Data amal usaha belum tersedia."),
            ("pcm:berita_list", b"Belum ada berita terbit."),
            ("pcm:unduhan", b"Belum ada dokumen untuk diunduh."),
        )
        for route, expected in checks:
            with self.subTest(route=route):
                self.assertContains(self.client.get(reverse(route)), expected.decode())

    def test_profile_page_shows_missing_field_messages(self):
        response = self.client.get(reverse("pcm:profil"))
        self.assertContains(response, "Profil organisasi belum tersedia.")
        self.assertContains(response, "Informasi tentang organisasi belum tersedia.")

    def test_admin_requires_authentication(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_project_stylesheet_is_discoverable(self):
        self.assertIsNotNone(find("css/style.css"))
        self.assertIsNotNone(find("img/Muhammadiyah.svg"))


class BeritaTests(TestCase):
    def create_news(self, *, status=Berita.Status.TERBIT, published_at=None, title="Berita"):
        return Berita.objects.create(
            judul=title,
            isi="Isi berita yang cukup untuk ditampilkan.",
            tanggal_terbit=published_at or timezone.now() - timedelta(hours=1),
            status=status,
        )

    def test_draft_and_future_news_are_hidden_and_return_404(self):
        draft = self.create_news(status=Berita.Status.DRAF, title="Draf rahasia")
        future = self.create_news(
            published_at=timezone.now() + timedelta(days=1),
            title="Berita masa depan",
        )

        self.assertEqual(
            self.client.get(reverse("pcm:berita_detail", args=[draft.slug])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("pcm:berita_detail", args=[future.slug])).status_code,
            404,
        )
        self.assertNotContains(self.client.get(reverse("pcm:berita_list")), "Draf rahasia")
        self.assertNotContains(self.client.get(reverse("pcm:berita_list")), "Berita masa depan")

    def test_duplicate_titles_receive_unique_automatic_slugs(self):
        first = self.create_news(title="Kabar PCM")
        second = self.create_news(title="Kabar PCM")
        self.assertEqual(first.slug, "kabar-pcm")
        self.assertEqual(second.slug, "kabar-pcm-2")

    def test_news_list_paginates_six_per_page(self):
        for index in range(7):
            self.create_news(title=f"Berita {index}")

        first_page = self.client.get(reverse("pcm:berita_list"))
        second_page = self.client.get(reverse("pcm:berita_list") + "?page=2")
        self.assertEqual(len(first_page.context["halaman"].object_list), 6)
        self.assertEqual(len(second_page.context["halaman"].object_list), 1)

    def test_news_search_only_returns_published_matches(self):
        self.create_news(title="Safari dakwah PCM")
        self.create_news(status=Berita.Status.DRAF, title="Safari dakwah draf")
        response = self.client.get(reverse("pcm:berita_list"), {"q": "safari"})
        self.assertContains(response, "Safari dakwah PCM")
        self.assertNotContains(response, "Safari dakwah draf")

    def test_published_manager_excludes_drafts_and_future_items(self):
        published = self.create_news(title="Terbit sekarang")
        self.create_news(status=Berita.Status.DRAF, title="Draf")
        self.create_news(
            published_at=timezone.now() + timedelta(days=1),
            title="Nanti",
        )
        self.assertEqual(list(Berita.objects.sudah_terbit()), [published])


class ContactTests(TestCase):
    def test_valid_contact_message_is_saved_and_success_is_shown(self):
        response = self.client.post(
            reverse("pcm:kontak"),
            {
                "nama": "Pengunjung PCM",
                "email": "pengunjung@example.com",
                "subjek": "Informasi kegiatan",
                "pesan": "Mohon informasi kegiatan organisasi.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("pcm:kontak"))
        self.assertEqual(PesanMasuk.objects.count(), 1)
        follow_up = self.client.get(reverse("pcm:kontak"))
        self.assertContains(follow_up, "Pesan Anda berhasil dikirim.")

    def test_invalid_contact_message_is_not_saved(self):
        response = self.client.post(
            reverse("pcm:kontak"),
            {
                "nama": "A",
                "email": "bukan-email",
                "subjek": "X",
                "pesan": "singkat",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PesanMasuk.objects.count(), 0)
        self.assertContains(response, "Nama harus terdiri dari minimal 2 karakter.")

    def test_contact_page_never_exposes_existing_messages(self):
        PesanMasuk.objects.create(
            nama="Pengirim Pribadi",
            email="private@example.com",
            subjek="Subjek rahasia PCM",
            pesan="Isi pesan rahasia yang hanya untuk admin.",
        )
        response = self.client.get(reverse("pcm:kontak"))
        self.assertNotContains(response, "Subjek rahasia PCM")
        self.assertNotContains(response, "Isi pesan rahasia")


class DownloadTests(TestCase):
    def test_document_page_and_endpoint_download_stored_file(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                document = Dokumen.objects.create(
                    judul="Dokumen organisasi",
                    berkas=SimpleUploadedFile("informasi.pdf", b"isi dokumen"),
                )
                page = self.client.get(reverse("pcm:unduhan"))
                self.assertContains(
                    page,
                    reverse("pcm:unduh_dokumen", args=[document.pk]),
                )

                response = self.client.get(
                    reverse("pcm:unduh_dokumen", args=[document.pk])
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("attachment", response["Content-Disposition"])
                self.assertEqual(b"".join(response.streaming_content), b"isi dokumen")


class AdminAndSeedTests(TestCase):
    def test_all_nine_models_are_registered_in_admin(self):
        expected_models = {
            Agenda,
            AmalUsaha,
            Berita,
            Dokumen,
            PesanMasuk,
            Pimpinan,
            ProfilOrganisasi,
            Ranting,
            TautanTerkait,
        }
        self.assertTrue(expected_models.issubset(admin.site._registry))

    def test_messages_are_read_only_in_admin(self):
        request = RequestFactory().get("/admin/pcm/pesanmasuk/")
        request.user = get_user_model()(is_staff=True, is_superuser=True)
        model_admin = admin.site._registry[PesanMasuk]
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))
        self.assertIn("pesan", model_admin.get_readonly_fields(request))

    def test_profile_is_a_singleton_and_admin_hides_second_add_action(self):
        ProfilOrganisasi.objects.create(nama="PCM Jebres", nama_singkat="PCM Jebres")
        request = RequestFactory().get("/admin/pcm/profilorganisasi/")
        request.user = get_user_model()(is_staff=True, is_superuser=True)
        model_admin = admin.site._registry[ProfilOrganisasi]
        self.assertFalse(model_admin.has_add_permission(request))
        with self.assertRaises(ValidationError):
            ProfilOrganisasi.objects.create(nama="Profil kedua", nama_singkat="Kedua")

    def test_seed_command_is_idempotent_and_does_not_overwrite_manual_edits(self):
        call_command("seed_pcm", stdout=StringIO())
        expected_counts = (1, 16, 13, 4)
        self.assertEqual(
            (
                ProfilOrganisasi.objects.count(),
                Pimpinan.objects.count(),
                Ranting.objects.count(),
                AmalUsaha.objects.count(),
            ),
            expected_counts,
        )

        ProfilOrganisasi.objects.filter(pk=1).update(nama="Nama yang diedit manual")
        call_command("seed_pcm", stdout=StringIO())
        self.assertEqual(
            (
                ProfilOrganisasi.objects.count(),
                Pimpinan.objects.count(),
                Ranting.objects.count(),
                AmalUsaha.objects.count(),
            ),
            expected_counts,
        )
        self.assertEqual(ProfilOrganisasi.objects.get(pk=1).nama, "Nama yang diedit manual")
        self.assertEqual(Berita.objects.count(), 0)
        self.assertEqual(Agenda.objects.count(), 0)
        self.assertEqual(Dokumen.objects.count(), 0)
        self.assertEqual(PesanMasuk.objects.count(), 0)
        self.assertEqual(TautanTerkait.objects.count(), 3)
