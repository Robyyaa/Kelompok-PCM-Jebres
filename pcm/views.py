from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from pathlib import Path

from .forms import PesanMasukForm
from .models import Agenda, AmalUsaha, Berita, Dokumen, Pimpinan, ProfilOrganisasi, Ranting


def home(request):
    profil = ProfilOrganisasi.objects.order_by("pk").first()

    context = {
        "active_page": "home",
        "profil": profil,
        "misi_list": (
            [baris.strip() for baris in profil.misi.splitlines() if baris.strip()]
            if profil
            else []
        ),
        "jumlah_anggota_ber_ktam": (
            str(profil.jumlah_anggota_ber_ktam)
            if profil and profil.jumlah_anggota_ber_ktam is not None
            else "Belum tersedia"
        ),
        "jumlah_ranting": Ranting.objects.count(),
        "jumlah_amal_usaha": AmalUsaha.objects.count(),
        "berita_terbaru": Berita.objects.sudah_terbit().order_by("-tanggal_terbit")[:3],
        "agenda_mendatang": Agenda.objects.filter(
            waktu_mulai__gte=timezone.now()
        ).order_by("waktu_mulai")[:3],
    }
    return render(request, "pcm/home.html", context)


def profil(request):
    data_profil = ProfilOrganisasi.objects.order_by("pk").first()
    context = {
        "active_page": "profil",
        "profil": data_profil,
        "misi_list": (
            [baris.strip() for baris in data_profil.misi.splitlines() if baris.strip()]
            if data_profil
            else []
        ),
    }
    return render(request, "pcm/profil.html", context)


def pimpinan(request):
    context = {
        "active_page": "pimpinan",
        "pimpinan_list": Pimpinan.objects.order_by("urutan_tampil", "nama"),
    }
    return render(request, "pcm/pimpinan.html", context)


def ranting(request):
    context = {
        "active_page": "ranting",
        "ranting_list": Ranting.objects.order_by("nama"),
    }
    return render(request, "pcm/ranting.html", context)


def amal_usaha(request):
    daftar = AmalUsaha.objects.order_by("bidang", "nama")
    kelompok = []
    for kode, label in AmalUsaha.Bidang.choices:
        items = [item for item in daftar if item.bidang == kode]
        if items:
            kelompok.append({"kode": kode, "label": label, "items": items})

    return render(
        request,
        "pcm/amal_usaha.html",
        {"active_page": "amal_usaha", "kelompok_amal_usaha": kelompok},
    )


def berita_list(request):
    queryset = Berita.objects.sudah_terbit().order_by("-tanggal_terbit")
    pencarian = request.GET.get("q", "").strip()
    if pencarian:
        queryset = queryset.filter(
            Q(judul__icontains=pencarian)
            | Q(ringkasan__icontains=pencarian)
            | Q(isi__icontains=pencarian)
        )

    paginator = Paginator(queryset, 6)
    halaman = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "pcm/berita_list.html",
        {
            "active_page": "berita",
            "halaman": halaman,
            "pencarian": pencarian,
        },
    )


def berita_detail(request, slug):
    berita = get_object_or_404(Berita.objects.sudah_terbit(), slug=slug)
    berita_lain = (
        Berita.objects.sudah_terbit()
        .exclude(pk=berita.pk)
        .order_by("-tanggal_terbit")[:3]
    )
    return render(
        request,
        "pcm/berita_detail.html",
        {"active_page": "berita", "berita": berita, "berita_lain": berita_lain},
    )


def agenda(request):
    sekarang = timezone.now()
    return render(
        request,
        "pcm/agenda.html",
        {
            "active_page": "agenda",
            "agenda_mendatang_list": Agenda.objects.filter(
                waktu_mulai__gte=sekarang
            ).order_by("waktu_mulai"),
            "agenda_terlaksana_list": Agenda.objects.filter(
                waktu_mulai__lt=sekarang
            ).order_by("-waktu_mulai"),
        },
    )


def unduhan(request):
    return render(
        request,
        "pcm/unduhan.html",
        {
            "active_page": "unduhan",
            "dokumen_list": Dokumen.objects.order_by("-waktu_unggah"),
        },
    )


def unduh_dokumen(request, pk):
    dokumen = get_object_or_404(Dokumen, pk=pk)
    if not dokumen.berkas or not dokumen.berkas.storage.exists(dokumen.berkas.name):
        raise Http404("Berkas dokumen tidak tersedia.")
    berkas = dokumen.berkas.open("rb")
    return FileResponse(
        berkas,
        as_attachment=True,
        filename=Path(dokumen.berkas.name).name,
    )


def kontak(request):
    profil = ProfilOrganisasi.objects.order_by("pk").first()
    if request.method == "POST":
        form = PesanMasukForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pesan Anda berhasil dikirim. Terima kasih.")
            return redirect("pcm:kontak")
    else:
        form = PesanMasukForm()

    return render(
        request,
        "pcm/kontak.html",
        {"active_page": "kontak", "profil": profil, "form": form},
    )
