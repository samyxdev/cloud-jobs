from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Jobs, CV

import uuid

def index(request):
    jobs = Jobs()
    context = {"jobs":jobs.get_jobs()}
    #context = {"jobs":hardcoded_jobs}

    return render(request, 'cv_match/index.html', context)

def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        user_file = request.FILES["file"]

        cv = CV()
        cv.handle_cv_upload(user_file, str(uuid.uuid4()))
        return render(request, 'cv_match/upload.html')
    else:
        return render(request, 'cv_match/upload.html')