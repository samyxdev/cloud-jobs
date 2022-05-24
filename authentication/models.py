from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(verbose_name='Title', null=True)
    company = models.TextField(verbose_name='Company', null=True)
    description = models.TextField(verbose_name='Description', null=True)
    link = models.TextField(verbose_name='link', null=True)


    def __str__(self):
        return self.user
        # TO RETURN THE DATA SAVED AND DISPLAY IT


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=10000, blank = True, null = True)
    category = models.CharField(max_length=10, blank = True, null = True)
    instructions = models.CharField(max_length=4000, blank = True, null = True)
    region = models.CharField(max_length=20, blank = True, null = True)
    slug = models.SlugField(default = 'test')
    image_url = models.CharField( max_length=10000, blank = True, null = True)

    def __str__(self):
        return self.name

        