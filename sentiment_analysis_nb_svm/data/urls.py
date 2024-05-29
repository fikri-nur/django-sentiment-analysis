from django.urls import path

from . import views

urlpatterns = [
    path('split_data_choose_method', views.indexView, name='index_view'),
    path('split_data/', views.split_data, name='split_data'),
    path('vectorize_data/', views.vectorize_data, name='vectorize_data'),
    path('train', views.indexTrainView, name='indexTrain_view'),
    path('test', views.indexTestView, name='indexTest_view'),
]
