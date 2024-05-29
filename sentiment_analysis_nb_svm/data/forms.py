# data/forms.py
from django import forms


class SplitDataPilihMetode(forms.Form):
    test_size = forms.ChoiceField(
        label="Persentase Data Uji",
        choices=[(str(i/10), str(i/10)) for i in range(1, 4)],
        initial='0.1',
        help_text="Pilih nilai antara 0.1 dan 0.3 dengan kelipatan 0.1",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    model = forms.ChoiceField(
        label="Pilih Model",
        choices=[
            ('naive_bayes', 'Naive Bayes'),
            ('svm', 'SVM'),
        ],
        initial='naive_bayes',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
