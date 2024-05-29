import json
import os
from django.shortcuts import render, redirect
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from wordcloud import WordCloud

from . import forms
from dataset.models import Dataset
from preprocessing.models import Preprocessing, WordCloud as WordCloudPath

def generate_word_cloud(text, output_path):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    wordcloud.to_file(output_path)

@login_required
def generate_wordcloud(request):
    if request.user.is_authenticated:
        # Get texts for word cloud
        positive_texts = ' '.join(
            Preprocessing.objects.filter(dataset__label="positif").values_list('stemmed_text', flat=True)
        )
        negative_texts = ' '.join(
            Preprocessing.objects.filter(dataset__label="negatif").values_list('stemmed_text', flat=True)
        )

        # Check and generate word cloud paths
        wordcloud_dir = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'wordclouds')
        os.makedirs(wordcloud_dir, exist_ok=True)
        
        def create_wordcloud(sentiment, text):
            wc_path = os.path.join(wordcloud_dir, f'{sentiment}_wordcloud.png')
            generate_word_cloud(text, wc_path)
            wc_path_obj = WordCloudPath.objects.filter(sentiment=sentiment).first()
            if wc_path_obj:
                wc_path_obj.path = wc_path
                wc_path_obj.save()
            else:
                WordCloudPath.objects.create(sentiment=sentiment, path=wc_path)

        create_wordcloud('positif', positive_texts)
        create_wordcloud('negatif', negative_texts)

        return redirect('index')
    else:
        return redirect("login")

@login_required
def index(request):
    if request.user.is_authenticated:
        # Count every label
        positif = Dataset.objects.filter(label="positif").count()
        negatif = Dataset.objects.filter(label="negatif").count()

        countEverySentiment = {
            "Positif": positif,
            "Negatif": negatif,
        }
        
        countEverySentiment_json = json.dumps(countEverySentiment)


        # Check if word cloud paths exist
        positive_wc_obj = WordCloudPath.objects.filter(sentiment='positif').first()
        negative_wc_obj = WordCloudPath.objects.filter(sentiment='negatif').first()

        if positive_wc_obj:
            positive_wordcloud_url = positive_wc_obj.path
        else:
            positive_wordcloud_url = 'img/default_wordcloud.png'

        if negative_wc_obj:
            negative_wordcloud_url = negative_wc_obj.path
        else:
            negative_wordcloud_url = 'img/default_wordcloud.png'
        
        check_wordcloud = None
        if positive_wordcloud_url == 'img/default_wordcloud.png' or negative_wordcloud_url == 'img/default_wordcloud.png':
            check_wordcloud = True
        context = {
            "title": "Dashboard",
            "countEveryLabel": [
                ["Positif", positif, "success"],
                ["Negatif", negatif, "danger"],
            ],
            "countEverySentiment": countEverySentiment,
            "countEverySentiment_json": countEverySentiment_json,
            "total": positif + negatif,
            "check_wordcloud": check_wordcloud,
            "positive_wordcloud_url": os.path.join('static', positive_wordcloud_url),
            "negative_wordcloud_url": os.path.join('static', negative_wordcloud_url),
        }

        return render(request, "index.html", context)
    else:
        return redirect("login")


def loginView(request):
    context = {}
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect("index")
        else:
            form = forms.LoginForm()
            context["form"] = form
            return render(request, "auth/login.html", context)

@login_required
def logoutView(request):
    if request.method == "POST":
        if "logout" in request.POST and request.POST["logout"] == "Submit":
            logout(request)
            return redirect("login")
    return redirect("login")


def register(request):
    context = {}
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            user = User.objects.create_user(
                username=register_form.cleaned_data["username"],
                email=register_form.cleaned_data["email"],
                password=register_form.cleaned_data["password1"],
            )
            user.save()
            return redirect("login")
        else:
            context["form"] = register_form
    else:
        form = forms.RegisterForm()
        context["form"] = form
    return render(request, "auth/register.html", context)
