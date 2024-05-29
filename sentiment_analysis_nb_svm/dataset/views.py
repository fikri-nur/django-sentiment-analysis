from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from .models import Dataset
from .forms import UploadFileForm

# Create your views here.
def index(request):
    context = {}
    if request.method == 'GET':
        form = UploadFileForm()
        datasets = Dataset.objects.all()
        context['title'] = 'Dataset'
        context['form'] = form
        context['datasets'] = datasets
    return render(request, 'dataset/index.html', context)

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
