from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(verbose_name='Title',)
    description = models.TextField(verbose_name='Description',)
    #company = models.TextField(verbose_name='Company',)

    #def __str__(self):
        # TO RETURN THE DATA SAVED AND DISPLAY IT


        