# naivebayes/urls.py
from django.urls import path
from . import views

app_name = 'naivebayes'

urlpatterns = [
    path('naive-bayes/', views.naiveBayesView, name='naive_bayes_view'),
    path('train_and_evaluate/', views.train_and_evaluate_model, name='train_and_evaluate'),
    path('predict_sentiment/', views.predict_sentiment, name='predict_sentiment'),
]