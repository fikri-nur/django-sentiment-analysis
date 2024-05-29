from django.db import models

# Create your models here.
class TrainData(models.Model):
    text = models.TextField()
    label = models.IntegerField()

class TestData(models.Model):
    text = models.TextField()
    label = models.IntegerField()
