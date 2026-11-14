from django import forms

from .models import PesanMasuk


class PesanMasukForm(forms.ModelForm):
    class Meta:
        model = PesanMasuk
        fields = ("nama", "email", "subjek", "pesan")
        labels = {
            "nama": "Nama",
            "email": "Email",
            "subjek": "Subjek",
            "pesan": "Pesan",
        }
        widgets = {
            "nama": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "subjek": forms.TextInput(),
            "pesan": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_nama(self):
        nama = self.cleaned_data["nama"].strip()
        if len(nama) < 2:
            raise forms.ValidationError("Nama harus terdiri dari minimal 2 karakter.")
        return nama

    def clean_subjek(self):
        subjek = self.cleaned_data["subjek"].strip()
        if len(subjek) < 3:
            raise forms.ValidationError("Subjek harus terdiri dari minimal 3 karakter.")
        return subjek

    def clean_pesan(self):
        pesan = self.cleaned_data["pesan"].strip()
        if len(pesan) < 10:
            raise forms.ValidationError("Pesan harus terdiri dari minimal 10 karakter.")
        return pesan
