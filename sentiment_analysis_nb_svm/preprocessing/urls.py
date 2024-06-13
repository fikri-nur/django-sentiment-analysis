from django.urls import path
from . import views

urlpatterns = [
    # Cleansing
    path("cleansing", views.cleansingView, name="cleansing_view"),
    path("process_cleaning", views.process_cleaning, name="process_cleaning"),
    # Casefolding
    path("casefolding", views.casefoldingView, name="casefolding_view"),
    path("process_casefolding", views.process_casefolding, name="process_casefolding"),
    # Normalization
    path("normalization", views.normalizationView, name="normalization_view"),
    path("process_normalization", views.process_normalization, name="process_normalization"),
    # Tokenization
    path("tokenization", views.tokenizationView, name="tokenization_view"),
    path("process_tokenization", views.process_tokenization, name="process_tokenization"),
    # Stopword
    path("stopword", views.stopwordView, name="stopword_view"),
    path("process_stopword", views.process_stopword, name="process_stopword"),
    # Stemming
    path("stemming", views.stemmingView, name="stemming_view"),
    path("process_stemming", views.process_stemming, name="process_stemming"),
]