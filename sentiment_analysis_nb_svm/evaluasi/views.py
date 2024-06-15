from django.shortcuts import render, redirect
from .models import Evaluation
import shutil
import pandas as pd
# Create your views here.

def indexView(request):
    evalDatas = Evaluation.objects.all()
    
    empty = True
    if len(evalDatas) > 0:
        empty = False
        
    for eval in evalDatas:
        eval.test_size = round(eval.test_size, 1)
        eval.train_size = round(eval.train_size, 1)
        eval.accuracy = round(eval.accuracy, 2)
        eval.precision = round(eval.precision, 2)
        eval.recall = round(eval.recall, 2)
        eval.f1_score = round(eval.f1_score, 2)
        
        eval.test_size = f"{eval.test_size * 100:.1f}".rstrip('0').rstrip('.')
        eval.train_size = f"{eval.train_size * 100:.1f}".rstrip('0').rstrip('.')
        eval.accuracy = f"{eval.accuracy * 100:.2f}".rstrip('0').rstrip('.')
        eval.precision = f"{eval.precision * 100:.2f}".rstrip('0').rstrip('.')
        eval.recall = f"{eval.recall * 100:.2f}".rstrip('0').rstrip('.')
        eval.f1_score = f"{eval.f1_score * 100:.2f}".rstrip('0').rstrip('.')
    context = {
        'evaluations': evalDatas,
        'empty': empty
    }
    return render(request, 'evaluasi/index.html', context)

def detailView(request, id):
    evalData = Evaluation.objects.get(id=id)
    evalData.test_size = round(evalData.test_size, 1)
    evalData.train_size = round(evalData.train_size, 1)
    evalData.accuracy = round(evalData.accuracy, 2)
    evalData.precision = round(evalData.precision, 2)
    evalData.recall = round(evalData.recall, 2)
    evalData.f1_score = round(evalData.f1_score, 2)
    
    evalData.test_size = f"{evalData.test_size * 100}%"
    evalData.train_size = f"{evalData.train_size * 100}%"
    evalData.accuracy = f"{evalData.accuracy * 100}%"
    evalData.precision = f"{evalData.precision * 100}%"
    evalData.recall = f"{evalData.recall * 100}%"
    evalData.f1_score = f"{evalData.f1_score * 100}%"
    
    
    evalData.confusion_matrix_path = evalData.confusion_matrix_path.replace("D:\\Kuliah\\Semester 8\\Sistem\\python\\sentiment_analysis_nb_svm\\pemodelan\\static", "")
    
    df = pd.read_csv(evalData.csv_path)
    # change df to queryset
    df = df.to_dict('records')
    return render(request, 'evaluasi/detail.html', {'evaluation': evalData, 'df': df})

def deleteView(request, id):
    evalData = Evaluation.objects.get(id=id)
    folder = evalData.confusion_matrix_path.replace("D:\\Kuliah\\Semester 8\\Sistem\\python\\sentiment_analysis_nb_svm\\pemodelan\\", "pemodelan/").replace("\\confusion_matrix.png", "")
    
    # Delete the folder and its content
    try:
        shutil.rmtree(folder)
    except Exception as e:
        print(f'Failed to delete {folder}. Reason: {e}')
    evalData.delete()
    return redirect('evaluasi:index_view')