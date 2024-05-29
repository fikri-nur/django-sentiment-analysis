from django.shortcuts import render
from .models import Evaluation
# Create your views here.

def indexView(request):
    evalDatas = Evaluation.objects.all()
    return render(request, 'evaluasi/index.html', {'evaluations': evalDatas})
