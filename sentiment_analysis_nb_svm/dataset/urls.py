from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_file, name="upload"),
    path("clear-all-data/", views.clear_all_data, name="clear-all-data"),
]