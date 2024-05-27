from django.db import models

# Create your models here.
class Dataset(models.Model):
    username = models.CharField(max_length=255)
    full_text = models.TextField()
    label = models.CharField(max_length=10)

    def __str__(self):
        # return all value from the object
        return str(self.id) + ' ' + self.username + ' ' + self.full_text + ' ' + self.label