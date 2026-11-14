from .models import ProfilOrganisasi, TautanTerkait


def pcm_global(request):
    return {
        "profil": ProfilOrganisasi.objects.order_by("pk").first(),
        "tautan_terkait": TautanTerkait.objects.order_by("urutan", "nama"),
    }
