from django.urls import path, register_converter

from . import views

class FloatConverter:
    regex = '[0-9]+\.[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return '%.2f' % value

register_converter(FloatConverter, 'float')

urlpatterns = [
    path('', views.indexView, name='index_view'),
    path('split_data/<float:test_size>/', views.split_data, name='split_data'),
    path('train', views.indexTrainView, name='indexTrain_view'),
    path('test', views.indexTestView, name='indexTest_view'),
]