from django.shortcuts import render

# Create your views here.
def indexView(request):
    return render(request, 'prediksi/index.html')

def prediksiView(request):
    return render(request, 'prediksi/prediksi.html')

def prediksi(request):
    return render(request, 'prediksi/prediksi.html')