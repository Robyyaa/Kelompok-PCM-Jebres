from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class ProfilOrganisasiQuerySet(models.QuerySet):
    def delete(self):
        raise ValidationError("Profil organisasi tidak dapat dihapus.")


class ProfilOrganisasi(models.Model):
    objects = ProfilOrganisasiQuerySet.as_manager()

    nama = models.CharField(max_length=200)
    nama_singkat = models.CharField(max_length=50)
    tagline = models.CharField(max_length=255, blank=True)
    tentang = models.TextField(blank=True)
    sejarah = models.TextField(blank=True)
    visi = models.TextField(blank=True)
    misi = models.TextField(blank=True)
    alamat_sekretariat = models.TextField(blank=True)
    telepon = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    jumlah_anggota_ber_ktam = models.PositiveIntegerField(null=True, blank=True)
    gambar_utama = models.ImageField(upload_to="profil/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    SINGLETON_PK = 1

    def clean(self):
        super().clean()
        if self.pk not in (None, self.SINGLETON_PK):
            raise ValidationError("Profil organisasi hanya boleh memiliki satu data.")
        if self.pk is None and type(self).objects.exclude(pk=self.SINGLETON_PK).exists():
            raise ValidationError("Profil organisasi hanya boleh memiliki satu data.")
        if self.pk is None and type(self).objects.filter(pk=self.SINGLETON_PK).exists():
            raise ValidationError("Profil organisasi sudah tersedia.")

    def save(self, *args, **kwargs):
        if self.pk not in (None, self.SINGLETON_PK):
            raise ValidationError("Profil organisasi hanya boleh memiliki satu data.")
        if self.pk is None:
            if type(self).objects.filter(pk=self.SINGLETON_PK).exists():
                raise ValidationError("Profil organisasi sudah tersedia.")
            self.pk = self.SINGLETON_PK
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Profil organisasi tidak dapat dihapus.")

    def __str__(self):
        return self.nama


class Pimpinan(models.Model):
    nama = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=100)
    periode = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to="pimpinan/", blank=True)
    urutan_tampil = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nama} — {self.jabatan}"


class Ranting(models.Model):
    nama = models.CharField(max_length=150)
    ketua = models.CharField(max_length=150, blank=True)
    alamat = models.TextField(blank=True)
    telepon = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama


class AmalUsaha(models.Model):
    class Bidang(models.TextChoices):
        PENDIDIKAN = "pendidikan", "Pendidikan"
        KESEHATAN = "kesehatan", "Kesehatan"
        SOSIAL = "sosial", "Sosial"
        EKONOMI = "ekonomi", "Ekonomi"

    nama = models.CharField(max_length=200)
    bidang = models.CharField(max_length=20, choices=Bidang.choices)
    deskripsi = models.TextField(blank=True)
    alamat = models.TextField(blank=True)
    gambar = models.ImageField(upload_to="amal_usaha/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nama} ({self.get_bidang_display()})"


class BeritaQuerySet(models.QuerySet):
    def sudah_terbit(self):
        return self.filter(
            status=Berita.Status.TERBIT,
            tanggal_terbit__lte=timezone.now(),
        )


class Berita(models.Model):
    class Status(models.TextChoices):
        DRAF = "draf", "Draf"
        TERBIT = "terbit", "Terbit"

    objects = BeritaQuerySet.as_manager()

    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    ringkasan = models.TextField(blank=True)
    isi = models.TextField()
    gambar_sampul = models.ImageField(upload_to="berita/", blank=True)
    tanggal_terbit = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAF,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _slug_unik(self):
        dasar = slugify(self.judul) or "berita"
        kandidat = dasar[: self._meta.get_field("slug").max_length]
        nomor = 2

        while type(self).objects.filter(slug=kandidat).exclude(pk=self.pk).exists():
            akhiran = f"-{nomor}"
            batas_dasar = self._meta.get_field("slug").max_length - len(akhiran)
            kandidat = f"{dasar[:batas_dasar]}{akhiran}"
            nomor += 1

        return kandidat

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._slug_unik()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


class Agenda(models.Model):
    nama_kegiatan = models.CharField(max_length=200)
    waktu_mulai = models.DateTimeField()
    tempat = models.CharField(max_length=200, blank=True)
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_kegiatan


class Dokumen(models.Model):
    judul = models.CharField(max_length=200)
    keterangan = models.TextField(blank=True)
    berkas = models.FileField(upload_to="dokumen/")
    waktu_unggah = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul


class PesanMasuk(models.Model):
    nama = models.CharField(max_length=150)
    email = models.EmailField()
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    waktu_kirim = models.DateTimeField(auto_now_add=True)
    sudah_dibaca = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subjek} — {self.nama}"


class TautanTerkait(models.Model):
    nama = models.CharField(max_length=100)
    url = models.URLField(max_length=500)
    urutan = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama
