from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required

import os
import shutil

from .models import Dataset
from data.models import TrainData, TestData
from preprocessing.models import Preprocessing, WordCloud
from evaluasi.models import Evaluation


@login_required
# Create your views here.
def index(request):
    context = {}
    if request.method == 'GET':
        form = UploadFileForm()
        datasets = Dataset.objects.all()
        context['title'] = 'Dataset'
        context['form'] = form
        context['datasets'] = datasets
        context['count'] = Dataset.objects.count()
    return render(request, 'dataset/index.html', context)

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file)
                print(df)
                for _, row in df.iterrows():
                    Dataset.objects.create(
                        username=row['username'],
                        full_text=row['full_text'],
                        label=row['label']
                    )
                messages.success(request, 'Data berhasil diimport.')
            except Exception as e:
                messages.error(request, f'Error saat mengimport data: {e}')
            return redirect('dataset:index')
    else:
        form = UploadFileForm()
    datasets = Dataset.objects.all()
    return render(request, 'dataset/index.html', {'form': form, 'datasets': datasets})

@login_required
def clear_all_data(request):
    Preprocessing.objects.all().delete()
    Dataset.objects.all().delete()
    TrainData.objects.all().delete()
    TestData.objects.all().delete()
    WordCloud.objects.all().delete()
    Evaluation.objects.all().delete()
    
    # JIka tabel wordcloud kosong, hapus wordcloud yang tersimpan dalam folder static/img/worclouds
    if WordCloud.objects.count() == 0:
        
        folder = 'static/img/wordclouds'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
                
    # Jika tabel evaluation kosong, hapus file yang tersimpan dalam folder pemodelan/static/naivebayes dan pemodelan/static/svm
    if Evaluation.objects.count() == 0:
        folder = 'pemodelan/static/naivebayes'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        
        folder = 'pemodelan/static/svm'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
                
    if Dataset.objects.count() == 0 or TrainData.objects.count() == 0 or TestData.objects.count() == 0 or Preprocessing.objects.count() == 0 or WordCloud.objects.count() == 0 or Evaluation.objects.count() == 0:
        messages.success(request, 'Semua data telah dihapus.')
    return redirect('dataset:index')