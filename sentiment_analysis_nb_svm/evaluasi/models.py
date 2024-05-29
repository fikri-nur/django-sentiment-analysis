from django.db import models

# Create your models here.
class Evaluation(models.Model):
    metode = models.CharField(max_length=255)
    test_size = models.FloatField()
    train_size = models.FloatField()
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    confusion_matrix_path = models.CharField(max_length=255)
    model_path = models.CharField(max_length=255)
    vectorizer_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Evaluation (test_size={self.test_size}, accuracy={self.accuracy}, created_at={self.created_at})"