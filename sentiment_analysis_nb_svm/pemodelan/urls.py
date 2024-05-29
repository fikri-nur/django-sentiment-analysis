# naivebayes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('naive-bayes/', views.naiveBayesView, name='naive_bayes_view'),
    path('train_and_evaluate_nb/', views.train_and_evaluate_nb, name='train_and_evaluate_nb'),
    path('svm/', views.svmView, name='svm_view'),
    path('train_and_evaluate_svm/', views.train_and_evaluate_svm, name='train_and_evaluate_svm'),
    path('predict_sentiment/', views.predict_sentiment, name='predict_sentiment'),
]