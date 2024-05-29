from django.contrib import admin
from django.urls import path, include

from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('generate_wordcloud/', views.generate_wordcloud, name='generate_wordcloud'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('register/', views.register, name='register'),
    path('dataset/', include(('dataset.urls', 'dataset'), namespace='dataset')),
    path('preprocessing/', include(('preprocessing.urls', 'preprocessing'), namespace='preprocessing')),
    path('data/', include(('data.urls', 'data'), namespace='data')),
    path('pemodelan/', include(('pemodelan.urls', 'pemodelan'), namespace='pemodelan')),
    path('evaluasi/', include(('evaluasi.urls', 'evaluasi'), namespace='evaluasi')),
    path('pengujian/', include(('pengujian.urls', 'pengujian'), namespace='pengujian')),
]
