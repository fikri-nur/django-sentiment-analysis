from django.shortcuts import render
from evaluasi.models import Evaluation
from data.models import TestData
import joblib


# Create your views here.
def indexView(request):
    evaluations = Evaluation.objects.all()
    return render(request, "pengujian/index.html", {"evaluations": evaluations})


def analisisTweet_view(request):
    evaluations = Evaluation.objects.all()
    return render(request, "pengujian/index-tweet.html", {"evaluations": evaluations})


def analysisSentimentView(request):
    evaluations = Evaluation.objects.all()
    results = []

    if request.method == "POST":
        model_id = request.POST.get("model_id")
        selected_evaluation = Evaluation.objects.get(id=model_id)

        if selected_evaluation:
            model = joblib.load(selected_evaluation.model_path)
            vectorizer = joblib.load(selected_evaluation.vectorizer_path)

            test_data = TestData.objects.all()
            for data in test_data:
                input_tfidf = vectorizer.transform([data.text]).toarray()
                prediction = model.predict(input_tfidf)[0]
                predicted_label = "Positif" if prediction == 1 else "Negatif"
                original_label = "Positif" if data.label == 1 else "Negatif"
                results.append(
                    {
                        "text": data.text,
                        "original_label": original_label,
                        "predicted_label": predicted_label,
                    }
                )

    return render(
        request,
        "pengujian/index-tweet.html",
        {"evaluations": evaluations, "results": results},
    )


def predictSentimentView(request):
    prediction = None
    evaluations = Evaluation.objects.all()

    if request.method == "POST":
        input_text = request.POST.get("input_text")
        model_id = request.POST.get("model_id")
        selected_evaluation = Evaluation.objects.get(id=model_id)

        if selected_evaluation:
            model = joblib.load(selected_evaluation.model_path)
            vectorizer = joblib.load(selected_evaluation.vectorizer_path)

            input_tfidf = vectorizer.transform([input_text]).toarray()
            prediction = model.predict(input_tfidf)[0]
            prediction = "Positif" if prediction == 1 else "Negatif"

    return render(
        request,
        "pengujian/index.html",
        {"prediction": prediction, "evaluations": evaluations},
    )
