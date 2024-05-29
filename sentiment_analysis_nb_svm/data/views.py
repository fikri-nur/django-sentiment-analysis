from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import SplitDataPilihModel

from .models import TrainData, TestData, TrainFeatures, TestFeatures
from dataset.models import Dataset
from preprocessing.models import Preprocessing

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
# Create your views here.
@login_required
def indexView(request):
    if request.method == 'POST':
        form = SplitDataPilihModel(request.POST)
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
        form = SplitDataPilihModel()

    return render(request, 'data/index.html', {'form': form})   

def split_data(test_size):
    test_size = float(test_size)
    preprocessings = Preprocessing.objects.all()
    stemmed_text = preprocessings.values_list('stemmed_text', flat=True)
    labels = Dataset.objects.filter(preprocessing__in=preprocessings).values_list('label', flat=True)
    
    labels = [0 if label == 'negatif' else 1 for label in labels]
    
    data_clean = pd.DataFrame({'stemmed_text': stemmed_text, 'label': labels})
    
    x = data_clean['stemmed_text']
    y = data_clean['label']
    
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)
    
    TrainData.objects.all().delete()
    TestData.objects.all().delete()
    
    TrainData.objects.bulk_create([TrainData(text=text, label=label) for text, label in zip(X_train, y_train)])
    TestData.objects.bulk_create([TestData(text=text, label=label) for text, label in zip(X_test, y_test)])


def indexTrainView(request):
    train_data = TrainData.objects.all()
    return render(request, 'train/index.html', {'train_data': train_data})

def indexTestView(request):
    test_data = TestData.objects.all()
    return render(request, 'test/index.html', {'test_data': test_data})

def vectorize_data(request):
    train_features = TrainFeatures.objects.all()
    test_features = TestFeatures.objects.all()
    
    X_train_tfidf = [np.frombuffer(feature.features, dtype=np.float64) for feature in train_features]
    y_train = [feature.label for feature in train_features]
    
    X_test_tfidf = [np.frombuffer(feature.features, dtype=np.float64) for feature in test_features]
    y_test = [feature.label for feature in test_features]
    
    # Calculate summary statistics
    X_train_summary = {
        'mean': np.mean(X_train_tfidf, axis=0),
        'std': np.std(X_train_tfidf, axis=0),
        'min': np.min(X_train_tfidf, axis=0),
        'max': np.max(X_train_tfidf, axis=0)
    }
    
    X_test_summary = {
        'mean': np.mean(X_test_tfidf, axis=0),
        'std': np.std(X_test_tfidf, axis=0),
        'min': np.min(X_test_tfidf, axis=0),
        'max': np.max(X_test_tfidf, axis=0)
    }
    
    context = {
        'X_train_summary': X_train_summary,
        'y_train': y_train,
        'X_test_summary': X_test_summary,
        'y_test': y_test,
    }
    
    return render(request, 'data/vectorize_data.html', context)

