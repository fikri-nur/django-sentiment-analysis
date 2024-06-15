from django.shortcuts import render
from evaluasi.models import Evaluation
from data.models import TestData
import joblib


# Create your views here.
def indexView(request):
    evalDatas = Evaluation.objects.all()
    
    empty = True
    if len(evalDatas) > 0:
        empty = False
    
    for eval in evalDatas:
        eval.test_size = round(eval.test_size, 1)
        eval.train_size = round(eval.train_size, 1)
        eval.accuracy = round(eval.accuracy, 2)
        eval.precision = round(eval.precision, 2)
        eval.recall = round(eval.recall, 2)
        eval.f1_score = round(eval.f1_score, 2)
        
        eval.test_size = f"{eval.test_size * 100:.1f}".rstrip('0').rstrip('.')
        eval.train_size = f"{eval.train_size * 100:.1f}".rstrip('0').rstrip('.')
        eval.accuracy = f"{eval.accuracy * 100:.2f}".rstrip('0').rstrip('.')
        eval.precision = f"{eval.precision * 100:.2f}".rstrip('0').rstrip('.')
        eval.recall = f"{eval.recall * 100:.2f}".rstrip('0').rstrip('.')
        eval.f1_score = f"{eval.f1_score * 100:.2f}".rstrip('0').rstrip('.')
    
    context = {
        'evaluations': evalDatas,
        'empty': empty
    }
    return render(request, "pengujian/index.html", context)


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
        
        selected_evaluation.test_size = round(selected_evaluation.test_size, 1)
        selected_evaluation.train_size = round(selected_evaluation.train_size, 1)
        selected_evaluation.accuracy = round(selected_evaluation.accuracy, 2)
        selected_evaluation.precision = round(selected_evaluation.precision, 2)
        selected_evaluation.recall = round(selected_evaluation.recall, 2)
        selected_evaluation.f1_score = round(selected_evaluation.f1_score, 2)
        
        selected_evaluation.test_size = f"{selected_evaluation.test_size * 100:.1f}".rstrip('0').rstrip('.')
        selected_evaluation.train_size = f"{selected_evaluation.train_size * 100:.1f}".rstrip('0').rstrip('.')
        selected_evaluation.accuracy = f"{selected_evaluation.accuracy * 100:.2f}".rstrip('0').rstrip('.')
        selected_evaluation.precision = f"{selected_evaluation.precision * 100:.2f}".rstrip('0').rstrip('.')
        selected_evaluation.recall = f"{selected_evaluation.recall * 100:.2f}".rstrip('0').rstrip('.')
        selected_evaluation.f1_score = f"{selected_evaluation.f1_score * 100:.2f}".rstrip('0').rstrip('.')
        
    return render(
        request,
        "pengujian/index.html",
        {"prediction": prediction, "evaluations": evaluations, 'input_text': input_text, 'model': selected_evaluation},
    )
