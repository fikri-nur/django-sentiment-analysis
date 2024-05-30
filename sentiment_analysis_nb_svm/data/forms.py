# data/forms.py
from django import forms


class SplitDataPilihMetode(forms.Form):
    pilihan = [
        ('0.1', '90% Data Latih - 10% Data Uji'),
        ('0.2', '80% Data Latih - 20% Data Uji'),
        ('0.3', '70% Data Latih - 30% Data Uji'),
    ]
    test_size = forms.ChoiceField(
        label="Persentase Data Latih dan Data Uji",
        choices=pilihan,
        initial='0.1',
        help_text="Pilih persentase data latih dan data uji",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    model = forms.ChoiceField(
        label="Pilih Model",
        choices=[
            ('naive_bayes', 'Naive Bayes'),
            ('svm', 'SVM'),
        ],
        initial='naive_bayes',
        help_text="Pilih model yang akan digunakan",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
