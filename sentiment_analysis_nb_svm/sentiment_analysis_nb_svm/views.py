import json
import os
import pandas as pd
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
from evaluasi.models import Evaluation

def generate_word_cloud(text, output_path):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    wordcloud.to_file(output_path)

@login_required
def generate_wordcloud(request):
    if request.user.is_authenticated:
        # Get texts for word cloud
        positive_texts = ' '.join(
            Preprocessing.objects.filter(dataset__label="positif").values_list('normalized_text', flat=True)
        )
        negative_texts = ' '.join(
            Preprocessing.objects.filter(dataset__label="negatif").values_list('normalized_text', flat=True)
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
        
        evalDatas = Evaluation.objects.all()
    
        empty = True
        if len(evalDatas) > 0:
            empty = False
            
        sentiment_counts = []
        for eval in evalDatas:
            eval.test_size = round(eval.test_size, 1)
            eval.train_size = round(eval.train_size, 1)
            
            eval.test_size = f"{eval.test_size * 100:.1f}".rstrip('0').rstrip('.')
            eval.train_size = f"{eval.train_size * 100:.1f}".rstrip('0').rstrip('.')
            # get csv data fro each evaluation
            csv = pd.read_csv(eval.csv_path)
            # Count positive and negative sentiment in predicted_label column
            count_positif = (csv['predicted_label'] == 'Positif').sum()
            count_negatif = (csv['predicted_label'] == 'Negatif').sum()
            # append the count to sentiment_counts
            sentiment_counts.append({
                'metode': eval.metode,
                'train_size': eval.train_size,
                'test_size': eval.test_size,
                'count_positif': count_positif,
                'count_negatif': count_negatif,
            })
        
        
        if os.path.exists("D:\\Kuliah\\Semester 8\\Sistem\\python\\sentiment_analysis_nb_svm\\data\\static\\csv\\test_data_info.csv"):
            csv_path = "D:\\Kuliah\\Semester 8\\Sistem\\python\\sentiment_analysis_nb_svm\\data\\static\\csv\\test_data_info.csv"
            manual_label = pd.read_csv(csv_path)
            # remove update_at column
            manual_label = manual_label.drop(columns=['updated_at'])
            # append the manual_label to sentiment_counts
            for i in range(len(manual_label)):
                sentiment_counts.append({
                    'metode': manual_label['metode'][i],
                    'train_size': manual_label['train_size'][i],
                    'test_size': manual_label['test_size'][i],
                    'count_positif': manual_label['count_positif'][i],
                    'count_negatif': manual_label['count_negatif'][i],
                })
        
        context = {
            "title": "Dashboard",
            "countEveryLabel": [
                ["Positif", positif, "primary"],
                ["Negatif", negatif, "danger"],
            ],
            "countEverySentiment": countEverySentiment,
            "countEverySentiment_json": countEverySentiment_json,
            "total": positif + negatif,
            "check_wordcloud": check_wordcloud,
            "positive_wordcloud_url": os.path.join('static', positive_wordcloud_url),
            "negative_wordcloud_url": os.path.join('static', negative_wordcloud_url),
            'empty': empty,
            'sentiments': sentiment_counts,
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
