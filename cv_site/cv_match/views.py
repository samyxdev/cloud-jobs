from django.http import HttpResponse
from django.shortcuts import render
from .models import Jobs

# Hardcoded listenings for example
hardcoded_jobs = [{"title":"Software Engineer", "desc":"Super position in a super company", "date":"22/05/2022"}, {"title":"Smart Contract Dev", "desc":"Solidity expert with 2+ years experience related to SC developpment.", "date":"20/05/2022"}]

def index(request):
    #jobs = Jobs()
    #context = {"jobs":jobs.get_jobs()}
    context = {"jobs":hardcoded_jobs}

    return render(request, 'cv_match/index.html', context)

def upload(request):
    return HttpResponse("Upload your CV here")