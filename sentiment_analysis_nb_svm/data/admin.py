from django.contrib import admin
from .models import TrainData, TestData, TrainFeatures, TestFeatures
# Register your models here.
admin.site.register(TrainData)
admin.site.register(TestData)
admin.site.register(TrainFeatures)
admin.site.register(TestFeatures)
