# naivebayes/views.py
import os
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data.models import TrainData, TestData, TrainFeatures, TestFeatures
from .models import Evaluation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import joblib

@login_required
def naiveBayesView(request):
    return render(request, 'naivebayes/index.html')

def train_and_evaluate_model(request):
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
    
    TrainFeatures.objects.all().delete()
    TestFeatures.objects.all().delete()
    
    TrainFeatures.objects.bulk_create([TrainFeatures(features=features, label=label) for features, label in zip(X_train_tfidf, y_train)])
    TestFeatures.objects.bulk_create([TestFeatures(features=features, label=label) for features, label in zip(X_test_tfidf, y_test)])

    
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
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negatif', 'Positif'], yticklabels=['Negatif', 'Positif'], ax=ax)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode('utf-8')
    
    # Create directory based on current time
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, "static/naivebayes/", now)
    os.makedirs(folder_path)
    
    # Save confusion matrix to file
    cm_path = os.path.join(folder_path, 'confusion_matrix.png')
    with open(cm_path, 'wb') as f:
        f.write(image_png)
    
    # Save model and vectorizer
    model_path = os.path.join(folder_path, 'naive_bayes_model.pkl')
    vectorizer_path = os.path.join(folder_path, 'tfidf_vectorizer.pkl')
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    # Save evaluation to database
    evaluation = Evaluation(
        test_size=len(X_test) / (len(X_train) + len(X_test)),
        train_size=len(X_train) / (len(X_train) + len(X_test)),
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        confusion_matrix_path=cm_path,
        model_path=model_path,
        vectorizer_path=vectorizer_path
    )
    evaluation.save()

    context = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': image_base64
    }
    
    return render(request, 'naivebayes/index.html', context)

def predict_sentiment(request):
    prediction = None
    
    if request.method == 'POST':
        input_text = request.POST.get('input_text')
        latest_evaluation = Evaluation.objects.latest('created_at')
        
        if latest_evaluation:
            model = joblib.load(latest_evaluation.model_path)
            vectorizer = joblib.load(latest_evaluation.vectorizer_path)
            
            input_tfidf = vectorizer.transform([input_text]).toarray()
            prediction = model.predict(input_tfidf)[0]
            prediction = 'Positif' if prediction == 1 else 'Negatif'
    
    return render(request, 'naivebayes/index.html', {'prediction': prediction})
