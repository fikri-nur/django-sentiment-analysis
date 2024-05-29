# data/forms.py
from django import forms


class SplitDataForm(forms.Form):
    test_size = forms.ChoiceField(
        label="Persentase Data Uji",
        choices=[(str(i/10), str(i/10)) for i in range(1, 10)],
        initial='0.2',
        help_text="Pilih nilai antara 0 dan 1 dengan kelipatan 0.1",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
