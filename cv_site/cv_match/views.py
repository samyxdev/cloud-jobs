from django.http import HttpResponse
from django.shortcuts import render

# Hardcoded listenings
jobs = [{"title":"Software Engineer", "desc":"Super position in a super company"}, {"title":"Smart Contract Dev", "desc":"Solidity expert with 2+ years experience related to SC developpment."}]

def index(request):
    context = {"jobs":jobs}
    return render(request, 'cv_match/index.html', context)

def upload(request):
    return HttpResponse("Upload your CV here")