import time

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
    read_stemming_words,
    apply_stemming,
    apply_sastrawi_stemming,
)

# Create your views here.


def process_cleaning(request):
    # Fetch all datasets
    datasets = Dataset.objects.all()
    for dataset in datasets:
        cleaned_text = clean_text(dataset.full_text)
        # Save the cleaned text to Preprocessing table
        preprocessing = Preprocessing.objects.create(
            dataset=dataset, cleaned_text=cleaned_text
        )
        preprocessing.save()
    return redirect("preprocessing:cleansing_view")


def cleansingView(request):
    datasets = Dataset.objects.all()
    preprocessings = Preprocessing.objects.all()
    context = {
        "title": "Cleansing Data",
        "datasets": datasets,
        "preprocessings": preprocessings,
    }
    return render(request, "preprocessing/cleansing.html", context)


def process_casefolding(request):
    preprocessings = Preprocessing.objects.all()
    for preprocessing in preprocessings:
        if preprocessing.case_folded_text is None:
            preprocessing.case_folded_text = case_folding(preprocessing.cleaned_text)
            preprocessing.save()
    return redirect("preprocessing:casefolding_view")


def casefoldingView(request):
    preprocessings = Preprocessing.objects.all()
    countBefore = preprocessings.filter(cleaned_text__isnull=True).count()
    countAfter = preprocessings.filter(case_folded_text__isnull=True).count()
    context = {
        "title": "Casefolding Data",
        "preprocessings": preprocessings,
        "countBefore": countBefore,
        "countAfter": countAfter,
    }
    return render(request, "preprocessing/case-folding.html", context)


def process_tokenization(request):
    preprocessings = Preprocessing.objects.all()
    for preprocessing in preprocessings:
        if preprocessing.tokenized_text is None:
            preprocessing.tokenized_text = tokenize_text(preprocessing.case_folded_text)
            preprocessing.save()
    return redirect("preprocessing:tokenization_view")


def tokenizationView(request):
    preprocessings = Preprocessing.objects.all()
    countBefore = preprocessings.filter(case_folded_text__isnull=True).count()
    countAfter = preprocessings.filter(tokenized_text__isnull=True).count()
    context = {
        "title": "Tokenization Data",
        "preprocessings": preprocessings,
        "countBefore": countBefore,
        "countAfter": countAfter,
    }
    return render(request, "preprocessing/tokenizing.html", context)

def process_normalization(request):
    preprocessings = Preprocessing.objects.all()
    slang_words = read_slang_words("file/normalization/slang_word_normalization.txt")
    for preprocessing in preprocessings:
        # Ensure tokenized_text is in list format
        tokenized_text = preprocessing.tokenized_text
        if (
            isinstance(tokenized_text, str)
            and tokenized_text.startswith("[")
            and tokenized_text.endswith("]")
        ):
            tokenized_text = literal_eval(tokenized_text)

        # Normalize text using slang words
        normalized_text = normalize_text_with_slang(tokenized_text, slang_words)

        # Save the normalized text as a token list
        preprocessing.normalized_text = normalized_text
        preprocessing.save()
    return redirect("preprocessing:normalization_view")


def normalizationView(request):
    preprocessings = Preprocessing.objects.all()
    countBefore = preprocessings.filter(tokenized_text__isnull=True).count()
    countAfter = preprocessings.filter(normalized_text__isnull=True).count()
    context = {
        "title": "Normalization Data",
        "preprocessings": preprocessings,
        "countBefore": countBefore,
        "countAfter": countAfter,
    }
    return render(request, "preprocessing/normalization.html", context)


def process_stopword(request):
    preprocessings = Preprocessing.objects.all()
    stopwords = read_stopwords("file/stopword/combined_stopwords.txt")
    for preprocessing in preprocessings:
        if preprocessing.stopwords_removed_text is None:
            normalized_text = preprocessing.normalized_text
            # Ubah normalized_text menjadi list jika perlu
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


def stopwordView(request):
    preprocessings = Preprocessing.objects.all()
    countBefore = preprocessings.filter(normalized_text__isnull=True).count()
    countAfter = preprocessings.filter(stopwords_removed_text__isnull=True).count()
    context = {
        "title": "Stopword Removal Data",
        "preprocessings": preprocessings,
        "countBefore": countBefore,
        "countAfter": countAfter,
    }
    return render(request, "preprocessing/stopword.html", context)


def process_stemming(request):
    preprocessings = Preprocessing.objects.all()
    stemming_words = read_stemming_words("file/stemming/words_stemming.txt")
    
    start_time = time.time()
    for preprocessing in preprocessings:
        if preprocessing.stemmed_text is None:
            stopwords_removed_text = preprocessing.stopwords_removed_text
            if isinstance(stopwords_removed_text, str) and stopwords_removed_text.startswith('[') and stopwords_removed_text.endswith(']'):
                stopwords_removed_text = literal_eval(stopwords_removed_text)
            
            # Apply stemming
            stemmed_text = apply_stemming(stopwords_removed_text, stemming_words)
            print(stemmed_text)
            # Save the stemmed text
            preprocessing.stemmed_text = stemmed_text
            preprocessing.save()
        else:
            preprocessing.stemmed_text = None
            preprocessing.save()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for custom stemming: {elapsed_time} seconds")
    return redirect("preprocessing:stemming_view")

def stemmingView(request):
    preprocessings = Preprocessing.objects.all()
    countBefore = preprocessings.filter(stopwords_removed_text__isnull=True).count()
    countAfter = preprocessings.filter(stemmed_text__isnull=True).count()
    context = {
        "title": "Stemming Data",
        "preprocessings": preprocessings,
        "countBefore": countBefore,
        "countAfter": countAfter,
    }
    return render(request, "preprocessing/stemming.html", context)

def process_stemming2(request):
    preprocessings = Preprocessing.objects.all()
    
    start_time = time.time()
    for preprocessing in preprocessings:
        if preprocessing.stemmed_text is None:
            # Apply Sastrawi stemming
            stemmed_text = apply_sastrawi_stemming(preprocessing.stopwords_removed_text)
            print(stemmed_text)
            # Save the stemmed text
            preprocessing.stemmed_text = stemmed_text
            preprocessing.save()
        else:
            preprocessing.stemmed_text = None
            preprocessing.save()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for Sastrawi stemming: {elapsed_time} seconds")
    return redirect("preprocessing:stemming_view")