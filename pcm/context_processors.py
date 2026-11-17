from .models import Agenda, Berita, PesanMasuk, ProfilOrganisasi, TautanTerkait


def pcm_global(request):
    return {
        "profil": ProfilOrganisasi.objects.order_by("pk").first(),
        "tautan_terkait": TautanTerkait.objects.order_by("urutan", "nama"),
    }


def pcm_admin_dashboard(request):
    match = getattr(request, "resolver_match", None)
    if not match or match.namespace != "admin" or match.url_name != "index":
        return {}
    if not getattr(request.user, "is_active", False) or not request.user.is_staff:
        return {}

    can_view_berita = request.user.has_perm("pcm.view_berita") or request.user.has_perm(
        "pcm.change_berita"
    )
    can_view_agenda = request.user.has_perm("pcm.view_agenda") or request.user.has_perm(
        "pcm.change_agenda"
    )
    can_view_pesan = request.user.has_perm("pcm.view_pesanmasuk") or request.user.has_perm(
        "pcm.change_pesanmasuk"
    )

    stats = {}
    if can_view_berita:
        stats.update(
            berita_total=Berita.objects.count(),
            berita_terbit=Berita.objects.filter(status=Berita.Status.TERBIT).count(),
            berita_draf=Berita.objects.filter(status=Berita.Status.DRAF).count(),
        )
    if can_view_agenda:
        stats["agenda_total"] = Agenda.objects.count()
    if can_view_pesan:
        stats["pesan_total"] = PesanMasuk.objects.count()

    return {
        "admin_stats": stats,
        "admin_can_view_berita": can_view_berita,
        "admin_can_view_agenda": can_view_agenda,
        "admin_can_view_pesan": can_view_pesan,
        "admin_can_add_berita": request.user.has_perm("pcm.add_berita"),
        "admin_can_add_agenda": request.user.has_perm("pcm.add_agenda"),
        "admin_recent_berita": Berita.objects.order_by("-updated_at", "-pk")[:5]
        if can_view_berita
        else (),
        "admin_recent_agenda": Agenda.objects.order_by("-waktu_mulai", "-pk")[:5]
        if can_view_agenda
        else (),
    }
