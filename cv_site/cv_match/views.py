from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Jobs, CV

import uuid

# Hardcoded listenings for example
hardcoded_jobs = [{"title":"Software Engineer",
                    "company":"TrustEn",
                    "desc":"Super position in a super company",
                    "date":"22/05/2022",
                    "location":"Barcelona",
                    "skills":["Ruby", "Python"]},

                    {"title":"Smart Contract Dev",
                    "company":"Slope.fi",
                    "desc":"Solidity expert with 2+ years experience related to SC developpment.",
                    "date":"20/05/2022",
                    "location":"Remote",
                    "skills":["Solidity"]}]

def index(request):
    #jobs = Jobs()
    #context = {"jobs":jobs.get_jobs()}
    context = {"jobs":hardcoded_jobs}

    return render(request, 'cv_match/index.html', context)

def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        user_file = request.FILES["file"]

        cv = CV()
        cv.handle_cv_upload(user_file, str(uuid.uuid4()))
        return render(request, 'cv_match/upload.html')
    else:
        return render(request, 'cv_match/upload.html')