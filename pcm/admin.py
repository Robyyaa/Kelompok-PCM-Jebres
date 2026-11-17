from django.contrib import admin
from django.db.models import F
from django.utils import formats

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


@admin.register(ProfilOrganisasi)
class ProfilOrganisasiAdmin(admin.ModelAdmin):
    list_display = ("nama", "nama_singkat", "email", "updated_at")
    search_fields = ("nama", "nama_singkat", "email")
    list_filter = ("updated_at",)
    ordering = ("nama",)

    def has_add_permission(self, request):
        return not ProfilOrganisasi.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pimpinan)
class PimpinanAdmin(admin.ModelAdmin):
    list_display = ("nama", "jabatan", "periode", "urutan_tampil")
    search_fields = ("nama", "jabatan", "periode")
    list_filter = ("periode",)
    ordering = ("urutan_tampil", "nama")


@admin.register(Ranting)
class RantingAdmin(admin.ModelAdmin):
    list_display = ("nama", "ketua", "telepon", "updated_at")
    search_fields = ("nama", "ketua", "alamat")
    ordering = ("nama",)


@admin.register(AmalUsaha)
class AmalUsahaAdmin(admin.ModelAdmin):
    list_display = ("nama", "bidang", "updated_at")
    search_fields = ("nama", "deskripsi", "alamat")
    list_filter = ("bidang",)
    ordering = ("bidang", "nama")


@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ("judul", "status", "tanggal_terbit_label", "updated_at")
    search_fields = ("judul", "ringkasan", "isi", "slug")
    list_filter = ("status", "tanggal_terbit")
    date_hierarchy = "tanggal_terbit"
    prepopulated_fields = {"slug": ("judul",)}
    ordering = (F("tanggal_terbit").desc(nulls_last=True), "-pk")

    @admin.display(description="Tanggal terbit", ordering="tanggal_terbit")
    def tanggal_terbit_label(self, obj):
        return formats.date_format(obj.tanggal_terbit, "DATETIME_FORMAT") if obj.tanggal_terbit else "Belum ditentukan"

    def save_model(self, request, obj, form, change):
        # Slug hasil prepopulasi admin tetap dibuat unik saat judul duplikat.
        if obj.slug and Berita.objects.filter(slug=obj.slug).exclude(pk=obj.pk).exists():
            obj.slug = ""
        super().save_model(request, obj, form, change)


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ("nama_kegiatan", "waktu_mulai", "tempat")
    search_fields = ("nama_kegiatan", "tempat", "keterangan")
    list_filter = ("waktu_mulai",)
    date_hierarchy = "waktu_mulai"
    ordering = ("-waktu_mulai",)


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ("judul", "waktu_unggah", "updated_at")
    search_fields = ("judul", "keterangan")
    list_filter = ("waktu_unggah",)
    date_hierarchy = "waktu_unggah"
    ordering = ("-waktu_unggah",)


@admin.register(PesanMasuk)
class PesanMasukAdmin(admin.ModelAdmin):
    list_display = ("subjek", "nama", "email", "waktu_kirim", "sudah_dibaca")
    search_fields = ("nama", "email", "subjek", "pesan")
    list_filter = ("sudah_dibaca", "waktu_kirim")
    date_hierarchy = "waktu_kirim"
    ordering = ("-waktu_kirim",)
    readonly_fields = tuple(field.name for field in PesanMasuk._meta.fields)
    actions = []

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TautanTerkait)
class TautanTerkaitAdmin(admin.ModelAdmin):
    list_display = ("nama", "url", "urutan")
    search_fields = ("nama", "url")
    ordering = ("urutan", "nama")


admin.site.site_header = "Admin Website PCM Jebres"
admin.site.site_title = "Admin PCM Jebres"
admin.site.index_title = "Pengelolaan Konten PCM Jebres"
