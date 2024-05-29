from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import SplitDataForm

from .models import TrainData, TestData 
from dataset.models import Dataset
from preprocessing.models import Preprocessing

import pandas as pd
from sklearn.model_selection import train_test_split

# Create your views here.
@login_required
def indexView(request):
    if request.method == 'POST':
        form = SplitDataForm(request.POST)
        if form.is_valid():
            test_size = form.cleaned_data['test_size']
            return redirect('data:split_data', test_size=test_size)
    else:
        form = SplitDataForm()

    return render(request, 'data/index.html', {'form': form})   

def split_data(request, test_size):
    # Ambil data dari model Django
    preprocessings = Preprocessing.objects.all()
    stemmed_text = preprocessings.values_list('stemmed_text', flat=True)
    labels = Dataset.objects.filter(preprocessing__in=preprocessings).values_list('label', flat=True)
    
    # Ubah label menjadi angka jika negatif menjadi 0, jika positif menjadi 1
    labels = [0 if label == 'negatif' else 1 for label in labels]
    
    # Gabungkan steam_text dan label menjadi satu tabel
    data_clean = pd.DataFrame({'stemmed_text': stemmed_text, 'label': labels})
    
    # Tentukan fitur (X) dan label (y)
    x = data_clean['stemmed_text']
    y = data_clean['label']
    
    # Bagi data menjadi data training dan data testing
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)
    
    # Simpan hasil split ke dalam database
    TrainData.objects.all().delete()  # Hapus data lama
    TestData.objects.all().delete()  # Hapus data lama
    
    TrainData.objects.bulk_create([TrainData(text=text, label=label) for text, label in zip(X_train, y_train)])
    TestData.objects.bulk_create([TestData(text=text, label=label) for text, label in zip(X_test, y_test)])
    
    context = {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'test_size': test_size
    }

    return render(request, 'data/split_data.html', context)


def indexTrainView(request):
    train_data = TrainData.objects.all()
    return render(request, 'train/index.html', {'train_data': train_data})

def indexTestView(request):
    test_data = TestData.objects.all()
    return render(request, 'test/index.html', {'test_data': test_data})