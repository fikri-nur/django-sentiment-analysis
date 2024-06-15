# naivebayes/views.py
import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from data.models import TrainData, TestData
from evaluasi.models import Evaluation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import joblib
import csv
import pandas as pd

@login_required
def naiveBayesView(request):
    train_data = TrainData.objects.all()
    test_data = TestData.objects.all()
    
    if len(train_data) == 0 or len(test_data) == 0:
        data = 0 
    else:
        data = 1
        
    context = {
        'title': 'Pemodelan Naive Bayes',
        'data': data,
    }
    return render(request, "naivebayes/index.html", context)


@login_required
def svmView(request):
    train_data = TrainData.objects.all()
    test_data = TestData.objects.all()
    
    # Get naive bayes evaluation data
    evalSVM = Evaluation.objects.filter(metode='SVM')
    
    # Ubah digit di belakang koma dan ubah menjadi persen (%)
    for eval in evalSVM:
        eval.test_size = round(eval.test_size, 1)
        eval.train_size = round(eval.train_size, 1)
        eval.accuracy = round(eval.accuracy, 2)
        eval.precision = round(eval.precision, 2)
        eval.recall = round(eval.recall, 2)
        eval.f1_score = round(eval.f1_score, 2)
        
        eval.test_size = f"{eval.test_size * 100}%"
        eval.train_size = f"{eval.train_size * 100}%"
        eval.accuracy = f"{eval.accuracy * 100}%"
        eval.precision = f"{eval.precision * 100}%"
        eval.recall = f"{eval.recall * 100}%"
        eval.f1_score = f"{eval.f1_score * 100}%"
        
    empty = True
    if len(evalSVM) > 0:
        empty = False
        
    context = {
        'empty': empty,
        'evaluations': evalSVM,
    }
    
    if len(train_data) == 0 or len(test_data) == 0:
        context['data'] = 0

    context['title'] = 'Pemodelan SVM'
    return render(request, "svm/index.html", context)


def train_and_evaluate_nb(request):
    # Ambil data dari model Django
    train_data = TrainData.objects.all()
    test_data = TestData.objects.all()

    X_train = [data.text for data in train_data]
    y_train = [data.label for data in train_data]
    X_test = [data.text for data in test_data]
    y_test = [data.label for data in test_data]
    
    # Vectorizer
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train).toarray()
    X_test_tfidf = vectorizer.transform(X_test).toarray()

    # Train Naive Bayes model
    model = MultinomialNB()
    model.fit(X_train_tfidf, y_train)

    # Predict on test data
    y_pred = model.predict(X_test_tfidf)    
    
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Plot confusion matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negatif", "Positif"],
        yticklabels=["Negatif", "Positif"],
        ax=ax,
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode("utf-8")

    # Create directory based on current time
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, "static/naivebayes/", now)
    os.makedirs(folder_path)
    
    # change array to predicted_label to list
    predicted_label = y_pred
    predicted_label = predicted_label.tolist()
    
    # change 1 to 'Positif' and 0 to 'Negatif'
    for i in range(len(predicted_label)):
        if predicted_label[i] == 1:
            predicted_label[i] = 'Positif'
        else:
            predicted_label[i] = 'Negatif'
    
    # change array to actual_label to list
    actual_label = y_test
    for i in range(len(actual_label)):
        if actual_label[i] == 1:
            actual_label[i] = 'Positif'
        else:
            actual_label[i] = 'Negatif'
    
    # export predicted_test_data to csv
    csv_path = os.path.join(folder_path, "predicted_test_data.csv")
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['text', 'actual_label', 'predicted_label'])
        for i in range(len(X_test)):
            writer.writerow([X_test[i], actual_label[i], predicted_label[i]])
    
    # Save confusion matrix to file
    cm_path = os.path.join(folder_path, "confusion_matrix.png")
    with open(cm_path, "wb") as f:
        f.write(image_png)

    # Save model and vectorizer
    model_path = os.path.join(folder_path, "naive_bayes_model.pkl")
    vectorizer_path = os.path.join(folder_path, "tfidf_vectorizer.pkl")
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    # Save evaluation to database
    evaluation = Evaluation(
        metode="Naive Bayes",
        test_size=len(X_test) / (len(X_train) + len(X_test)),
        train_size=len(X_train) / (len(X_train) + len(X_test)),
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        confusion_matrix_path=cm_path,
        model_path=model_path,
        vectorizer_path=vectorizer_path,
    )
    evaluation.save()
    
    latest_evaluation = Evaluation.objects.latest("created_at")
    cm_path = latest_evaluation.confusion_matrix_path
    cm_path = cm_path.replace(current_dir, "").replace("\\", "/").replace("/static/", "")
    
    # Ubah digit di belakang koma
    latest_evaluation.test_size = round(latest_evaluation.test_size, 1)
    latest_evaluation.train_size = round(latest_evaluation.train_size, 1)
    latest_evaluation.accuracy = round(latest_evaluation.accuracy, 2)
    latest_evaluation.precision = round(latest_evaluation.precision, 2)
    latest_evaluation.recall = round(latest_evaluation.recall, 2)
    latest_evaluation.f1_score = round(latest_evaluation.f1_score, 2)
    
    # Ubah menjadi persen (%)
    latest_evaluation.test_size = f"{latest_evaluation.test_size * 100}%"
    latest_evaluation.train_size = f"{latest_evaluation.train_size * 100}%"
    latest_evaluation.accuracy = f"{latest_evaluation.accuracy * 100}%"
    latest_evaluation.precision = f"{latest_evaluation.precision * 100}%"
    latest_evaluation.recall = f"{latest_evaluation.recall * 100}%"
    latest_evaluation.f1_score = f"{latest_evaluation.f1_score * 100}%"

        
    df = pd.read_csv(csv_path)
    # change df to queryset
    df = df.to_dict('records')
    context = {
        'title': 'Pemodelan Naive Bayes',
        'isTrue': True,
        'metode': latest_evaluation.metode,
        'test_size': latest_evaluation.test_size,
        'train_size': latest_evaluation.train_size,
        "accuracy": latest_evaluation.accuracy,
        "precision": latest_evaluation.precision,
        "recall": latest_evaluation.recall,
        "f1_score": latest_evaluation.f1_score,
        "created_at": latest_evaluation.created_at,
        "confusion_matrix": cm_path,
        "df": df,
    }

    return render(request, "naivebayes/index.html", context)


def train_and_evaluate_svm(request):
    # Ambil data dari model Django
    train_data = TrainData.objects.all()
    test_data = TestData.objects.all()

    X_train = [data.text for data in train_data]
    y_train = [data.label for data in train_data]
    X_test = [data.text for data in test_data]
    y_test = [data.label for data in test_data]

    # Vectorizer
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train).toarray()
    X_test_tfidf = vectorizer.transform(X_test).toarray()
    
    # Hyperparameter tuning for LinearSVC
    best_accuracy = 0
    best_c = 0
    for c in [0.01, 0.05, 0.25, 0.5, 0.75, 1]:
        model = SVC(C=c)
        model.fit(X_train_tfidf, y_train)
        y_pred = model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_c = c

    # Train SVM model
    model = SVC(C=best_c)
    model.fit(X_train_tfidf, y_train)

    # Predict on test data
    y_pred = model.predict(X_test_tfidf)
    
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Plot confusion matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negatif", "Positif"],
        yticklabels=["Negatif", "Positif"],
        ax=ax,
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode("utf-8")

    # Create directory based on current time
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, "static/svm/", now)
    os.makedirs(folder_path)

    # Save confusion matrix to file
    cm_path = os.path.join(folder_path, "confusion_matrix.png")
    with open(cm_path, "wb") as f:
        f.write(image_png)
        
    # Save model and vectorizer
    model_path = os.path.join(folder_path, "svm_model.pkl")
    vectorizer_path = os.path.join(folder_path, "tfidf_vectorizer.pkl")
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    
    # Save evaluation to database
    evaluation = Evaluation(
        metode="SVM",
        test_size=len(X_test) / (len(X_train) + len(X_test)),
        train_size=len(X_train) / (len(X_train) + len(X_test)),
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        confusion_matrix_path=cm_path,
        model_path=model_path,
        vectorizer_path=vectorizer_path,
    )
    evaluation.save()

    latest_evaluation = Evaluation.objects.latest("created_at")
    cm_path = latest_evaluation.confusion_matrix_path
    cm_path = cm_path.replace(current_dir, "").replace("\\", "/").replace("/static/", "")
    
    # Ubah digit di belakang koma
    latest_evaluation.test_size = round(latest_evaluation.test_size, 1)
    latest_evaluation.train_size = round(latest_evaluation.train_size, 1)
    latest_evaluation.accuracy = round(latest_evaluation.accuracy, 2)
    latest_evaluation.precision = round(latest_evaluation.precision, 2)
    latest_evaluation.recall = round(latest_evaluation.recall, 2)
    latest_evaluation.f1_score = round(latest_evaluation.f1_score, 2)
    
    # Ubah menjadi persen (%)
    latest_evaluation.test_size = f"{latest_evaluation.test_size * 100}%"
    latest_evaluation.train_size = f"{latest_evaluation.train_size * 100}%"
    latest_evaluation.accuracy = f"{latest_evaluation.accuracy * 100}%"
    latest_evaluation.precision = f"{latest_evaluation.precision * 100}%"
    latest_evaluation.recall = f"{latest_evaluation.recall * 100}%"
    latest_evaluation.f1_score = f"{latest_evaluation.f1_score * 100}%"
    
    evalSVM = Evaluation.objects.filter(metode='SVM')
    # Ubah digit di belakang koma dan ubah menjadi persen (%)
    for eval in evalSVM:
        eval.test_size = round(eval.test_size, 1)
        eval.train_size = round(eval.train_size, 1)
        eval.accuracy = round(eval.accuracy, 2)
        eval.precision = round(eval.precision, 2)
        eval.recall = round(eval.recall, 2)
        eval.f1_score = round(eval.f1_score, 2)
        
        eval.test_size = f"{eval.test_size * 100}%"
        eval.train_size = f"{eval.train_size * 100}%"
        eval.accuracy = f"{eval.accuracy * 100}%"
        eval.precision = f"{eval.precision * 100}%"
        eval.recall = f"{eval.recall * 100}%"
        eval.f1_score = f"{eval.f1_score * 100}%"
        
    empty = True
    if len(evalSVM) > 0:
        empty = False
        
    context = {
        'title': 'Pemodelan Naive Bayes',
        'empty': empty,
        'evaluations': evalSVM,
        'isTrue': True,
        'metode': latest_evaluation.metode,
        'test_size': latest_evaluation.test_size,
        'train_size': latest_evaluation.train_size,
        "accuracy": latest_evaluation.accuracy,
        "precision": latest_evaluation.precision,
        "recall": latest_evaluation.recall,
        "f1_score": latest_evaluation.f1_score,
        "created_at": latest_evaluation.created_at,
        "confusion_matrix": cm_path,
    }

    return render(request, "svm/index.html", context)
