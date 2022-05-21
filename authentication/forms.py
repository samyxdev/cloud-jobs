from .models import JobDescription
from django import forms


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['title', 'description']
        #fields = "__all__"