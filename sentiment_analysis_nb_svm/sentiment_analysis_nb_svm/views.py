from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import forms
from dataset.models import Dataset

def index(request):
    if request.user.is_authenticated:
        # countevery label
        positif = Dataset.objects.filter(label="positif").count()
        negatif = Dataset.objects.filter(label="negatif").count()
        netral = Dataset.objects.filter(label="netral").count()
        
        countEverySentiment = {
            "Positif": positif,
            "Negatif": negatif,
            "Netral": netral
        }

        context = {
            "title": "Dashboard",
            "countEveryLabel": [
                ["Positif", positif, "success"],
                ["Negatif", negatif, "danger"],
                ["Netral", netral, "primary"],
            ],
            "countEverySentiment": countEverySentiment,
            "total": positif + negatif + netral,
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
