from django.db import models
from dataset.models import Dataset

# Create your models here.
class Preprocessing(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cleaned_text = models.TextField(null=True, blank=True)
    case_folded_text = models.TextField(null=True, blank=True)
    normalized_text = models.TextField(null=True, blank=True)
    tokenized_text = models.TextField(null=True, blank=True)
    stopwords_removed_text = models.TextField(null=True, blank=True)
    stemmed_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} {self.dataset_id}"

class WordCloud(models.Model):
    sentiment = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.sentiment} {self.path}"
