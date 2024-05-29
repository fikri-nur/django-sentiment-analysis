from django.urls import path

from . import views

urlpatterns = [
    path('prediksi_sentiment', views.indexView, name='index_view'),
    path('predict_sentiment/', views.predictSentimentView, name='predict_sentiment_view'),
    path('analisis_tweet/', views.analisisTweet_view, name='analisisTweet_view'),
    path('analysis_sentiment/', views.analysisSentimentView, name='analysis_sentiment_view'),
]