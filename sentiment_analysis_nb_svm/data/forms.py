# data/forms.py
from django import forms


class SplitDataForm(forms.Form):
    test_size = forms.FloatField(
        label="Persentase Data Uji",
        min_value=0.0,
        max_value=1.0,
        initial=0.2,
        help_text="Masukkan nilai antara 0 dan 1",
    )
