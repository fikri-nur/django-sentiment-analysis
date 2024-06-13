from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexView, name='index_view'),
    path('detail/<int:id>', views.detailView, name='detail_view'),
    path('delete/<int:id>', views.deleteView, name='delete_view')
]