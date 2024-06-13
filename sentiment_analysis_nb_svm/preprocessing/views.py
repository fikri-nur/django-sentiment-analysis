import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dataset.models import Dataset
from .models import Preprocessing
from ast import literal_eval

from .utils import (
    clean_text,
    case_folding,
    tokenize_text,
    read_slang_words,
    normalize_text_with_slang,
    read_stopwords,
    remove_stopwords,
    apply_sastrawi_stemming,
)

# Create your views here.

@login_required
def process_cleaning(request):
    # Fetch all datasets
    datasets = Dataset.objects.all()
    for dataset in datasets:
        cleaned_text = clean_text(dataset.full_text)
        preprocessing = Preprocessing.objects.create(
            dataset=dataset, cleaned_text=cleaned_text
        )
        preprocessing.save()
    return redirect("preprocessing:cleansing_view")

@login_required
def cleansingView(request):
    datasets = Dataset.objects.all()
    preprocessings = Preprocessing.objects.all()
    context = {
        "title": "Cleansing Data",
        "datasets": datasets,
        "preprocessings": preprocessings,
    }
    return render(request, "preprocessing/cleansing.html", context)

@login_required
def process_casefolding(request):
    preprocessings = Preprocessing.objects.all()
    for preprocessing in preprocessings:
        if preprocessing.case_folded_text is None:
            preprocessing.case_folded_text = case_folding(preprocessing.cleaned_text)
            preprocessing.save()
    return redirect("preprocessing:casefolding_view")

@login_required
def casefoldingView(request):
    preprocessings = Preprocessing.objects.all()
    countCleanedText = preprocessings.filter(cleaned_text__isnull=False).count()
    countCaseFoldedText = preprocessings.filter(case_folded_text__isnull=False).count()
    context = {
        "title": "Casefolding Data",
        "preprocessings": preprocessings,
        "countCleanedText": countCleanedText,
        "countCaseFoldedText": countCaseFoldedText,
    }
    return render(request, "preprocessing/case-folding.html", context)

def process_normalization(request):
    preprocessings = Preprocessing.objects.all()
    slang_words = read_slang_words("static/normalization/slang_word_normalization.txt")
    for preprocessing in preprocessings:
        if preprocessing.normalized_text is None:
            normalized_text = normalize_text_with_slang(preprocessing.case_folded_text, slang_words)
            preprocessing.normalized_text = normalized_text
            preprocessing.save()
    return redirect("preprocessing:normalization_view")

@login_required
def normalizationView(request):
    preprocessings = Preprocessing.objects.all()
    countCaseFoldedText = preprocessings.filter(case_folded_text__isnull=False).count()
    countNormalizedText = preprocessings.filter(normalized_text__isnull=False).count()
    context = {
        "title": "Normalization Data",
        "preprocessings": preprocessings,
        "countCaseFoldedText": countCaseFoldedText,
        "countNormalizedText": countNormalizedText,
    }
    return render(request, "preprocessing/normalization.html", context)

@login_required
def process_tokenization(request):
    preprocessings = Preprocessing.objects.all()
    for preprocessing in preprocessings:
        if preprocessing.tokenized_text is None:
            preprocessing.tokenized_text = tokenize_text(preprocessing.normalized_text)
            preprocessing.save()
    return redirect("preprocessing:tokenization_view")

@login_required
def tokenizationView(request):
    preprocessings = Preprocessing.objects.all()
    countNormalizedText = preprocessings.filter(normalized_text__isnull=False).count()
    countTokenizedText = preprocessings.filter(tokenized_text__isnull=False).count()
    context = {
        "title": "Tokenization Data",
        "preprocessings": preprocessings,
        "countNormalizedText": countNormalizedText,
        "countTokenizedText": countTokenizedText,
    }
    return render(request, "preprocessing/tokenizing.html", context)

@login_required
def process_stopword(request):
    preprocessings = Preprocessing.objects.all()
    stopwords = read_stopwords("static/stopword/combined_stopwords.txt")
    for preprocessing in preprocessings:
        if preprocessing.stopwords_removed_text is None:
            normalized_text = preprocessing.normalized_text
            if (
                isinstance(normalized_text, str)
                and normalized_text.startswith("[")
                and normalized_text.endswith("]")
            ):
                normalized_text = literal_eval(normalized_text)

            stopwords_removed_text = remove_stopwords(normalized_text, stopwords)
            preprocessing.stopwords_removed_text = stopwords_removed_text
            preprocessing.save()
    return redirect("preprocessing:stopword_view")

@login_required
def stopwordView(request):
    preprocessings = Preprocessing.objects.all()
    countTokenizedText = preprocessings.filter(tokenized_text__isnull=False).count()
    countStopWordText = preprocessings.filter(stopwords_removed_text__isnull=False).count()
    context = {
        "title": "Stopword Removal Data",
        "preprocessings": preprocessings,
        "countTokenizedText": countTokenizedText,
        "countStopWordText": countStopWordText,
    }
    return render(request, "preprocessing/stopword.html", context)

@login_required
def process_stemming(request):
    preprocessings = Preprocessing.objects.all()
    
    start = time.time()
    for preprocessing in preprocessings:
        if preprocessing.stemmed_text is None:
            stemmed_text = apply_sastrawi_stemming(preprocessing.stopwords_removed_text)
            preprocessing.stemmed_text = stemmed_text
            preprocessing.save()
        else:
            preprocessing.stemmed_text = None
            preprocessing.save()
    end = time.time()
    elapsed_time = end - start
    # Convert to minutes if elapsed time more than 60 seconds
    if elapsed_time > 60:
        elapsed_time = elapsed_time / 60
        # Jika ada angka dibelakang koma maka ubah angka tersebut menjadi detiknya
        if (elapsed_time % 1) != 0:
            elapsed_time = f"{int(elapsed_time)} minutes {int((elapsed_time % 1) * 60)} seconds"
    print(f"Elapsed time: {elapsed_time}")
    return redirect("preprocessing:stemming_view")

@login_required
def stemmingView(request):
    preprocessings = Preprocessing.objects.all()
    countStopWordText = preprocessings.filter(stopwords_removed_text__isnull=False).count()
    countStemmedText = preprocessings.filter(stemmed_text__isnull=False).count()
    context = {
        "title": "Stemming Data",
        "preprocessings": preprocessings,
        "countStopWordText": countStopWordText,
        "countStemmedText": countStemmedText,
    }
    return render(request, "preprocessing/stemming.html", context)