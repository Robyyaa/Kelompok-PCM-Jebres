from django import template

register = template.Library()

GROUPS = (
    ("Konten", ("Berita", "Agenda", "Dokumen")),
    ("Organisasi", ("ProfilOrganisasi", "Pimpinan", "Ranting", "AmalUsaha")),
    ("Lainnya", ("PesanMasuk", "TautanTerkait")),
    ("Akses", ("User", "Group")),
)


@register.simple_tag
def pcm_admin_nav_groups(app_list):
    models = [model for app in app_list for model in app.get("models", [])]
    for model in models:
        model["nav_url"] = model.get("admin_url") or model.get("add_url")
    grouped = []
    included = set()
    for title, names in GROUPS:
        items = [model for model in models if model.get("object_name") in names]
        if items:
            grouped.append({"title": title, "items": items})
            included.update(model.get("object_name") for model in items)
    extras = [model for model in models if model.get("object_name") not in included]
    if extras:
        grouped.append({"title": "Model lainnya", "items": extras})
    return grouped
