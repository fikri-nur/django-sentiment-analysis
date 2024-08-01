from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import SplitDataPilihMetode

from .models import TrainData, TestData
from dataset.models import Dataset
from preprocessing.models import Preprocessing

import pandas as pd
import numpy as np
import os
import csv

from sklearn.model_selection import train_test_split
# Create your views here.
@login_required
def indexView(request):
    # Ambil kolom stemmed_text dari tabel Preprocessing
    preprocessings = Preprocessing.objects.all()
    stemmed_text = preprocessings.values_list('stemmed_text', flat=True)
    countStemmedText = stemmed_text.count()
    empty = True
    if countStemmedText != 0:
        empty = False
    context = {
        'title': 'Bagi Data dan Pilih Metode',
        'empty': empty,
        
    }
    if request.method == 'POST':
        form = SplitDataPilihMetode(request.POST)
        if form.is_valid():
            test_size = form.cleaned_data['test_size']
            model = form.cleaned_data['model']
            split_data(test_size)
            if model == 'naive_bayes':
                return redirect('pemodelan:naive_bayes_view')
            elif model == 'svm':
                return redirect('pemodelan:svm_view')
            return redirect('data:indexTest_view')
    else:
        form = SplitDataPilihMetode()
        
    context['form'] = form
    return render(request, 'data/index.html', context)   

def split_data(test_size):
    test_size = float(test_size)
    preprocessings = Preprocessing.objects.all()
    stemmed_text = preprocessings.values_list('stemmed_text', flat=True)
    labels = Dataset.objects.filter(preprocessing__in=preprocessings).values_list('label', flat=True)
    
    labels = [0 if label == 'negatif' else 1 for label in labels]
    
    data_clean = pd.DataFrame({'stemmed_text': stemmed_text, 'label': labels})
    
    x = data_clean['stemmed_text']
    y = data_clean['label']
    
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=17)
    
    TrainData.objects.all().delete()
    TestData.objects.all().delete()
    
    TrainData.objects.bulk_create([TrainData(text=text, label=label) for text, label in zip(X_train, y_train)])
    TestData.objects.bulk_create([TestData(text=text, label=label) for text, label in zip(X_test, y_test)])
    
    # Menyimpan informasi data test ke dalam csv
    # get the test data
    test_data = TestData.objects.all()
    # change to dataframe
    df = pd.DataFrame({'label': [data.label for data in test_data]})
    # change label to Positif and Negatif
    df['label'] = np.where(df['label'] == 1, 'Positif', 'Negatif')
    count_positif = (df['label'] == 'Positif').sum()
    count_negatif = (df['label'] == 'Negatif').sum()
    
    # get the test_size and train_size
    train_size = 1 - test_size
    test_size = test_size * 100
    train_size = train_size * 100
    
    test_size = int(test_size)
    train_size = int(train_size)
    
    # Get the current directory and the folder path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, "static/csv/")
    
    # check if the csv file is already created
    csv_path = os.path.join(folder_path, "test_data_info.csv")
    if not os.path.exists(csv_path):
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['metode', 'train_size', 'test_size', 'count_positif', 'count_negatif', 'updated_at'])
            writer.writerow(['Manual', train_size, test_size, count_positif, count_negatif, pd.Timestamp.now()])
    else:
        # check if the test_size is already in the csv file, if yes, then update the count_positif and count_negatif
        data_csv = pd.read_csv(csv_path)
        if test_size in data_csv['test_size'].values:
            data_csv.loc[data_csv['test_size'] == test_size, 'count_positif'] = count_positif
            data_csv.loc[data_csv['test_size'] == test_size, 'count_negatif'] = count_negatif
            data_csv.loc[data_csv['test_size'] == test_size, 'updated_at'] = pd.Timestamp.now()
            data_csv.to_csv(csv_path, index=False)
        else:
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Manual', train_size, test_size, count_positif, count_negatif, pd.Timestamp.now()])
        


def indexTrainView(request):
    train_data = TrainData.objects.all()
    countTrainData = train_data.count()
    empty = True
    if countTrainData != 0:
        empty = False
    context = {
        'title': 'Data Training',
        'train_data': train_data,
        'empty': empty,
    }
    return render(request, 'train/index.html', context)

def indexTestView(request):
    test_data = TestData.objects.all()
    countTestData = test_data.count()
    empty = True
    if countTestData != 0:
        empty = False
    context = {
        'title': 'Data Testing',
        'test_data': test_data,
        'empty': empty,
    }
    return render(request, 'test/index.html', context)

