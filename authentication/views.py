from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

import requests
import ast
import uuid
#from .forms import JobDescriptionForm
#from .models import Meal
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Jobs, CV



def index(request):
    jobs = Jobs()
    context = {"jobs":jobs.get_jobs()}
    #context = {"jobs":hardcoded_jobs}

    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password =password)

        if user is not None:
            auth.login(request , user)
            return redirect('/')    
        else:
            messages.info(request, 'invalid username or password')
            return redirect("/login")
    else:
        return render(request,'login.html')


def register(request):

    if request.method == 'POST':

        email = request.POST['email']
        username = request.POST['username']
        password= request.POST['password']


        user = User.objects.create_user(username = username , password = password , email = email)
        user.save()
        print('user created')
        return redirect('/')

    return render(request,'register.html')

#def cv(request):
#    return render(request, 'cv.html')
def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        user_file = request.FILES["file"]

        cv = CV()
        cv.handle_cv_upload(user_file, str(uuid.uuid4()))
        return render(request, 'upload.html')
    else:
        return render(request, 'upload.html')


def home(request):
    jobs = {}
    if 'jobname' in request.GET:
        name = request.GET['jobname']
        url = 'https://www.themealdb.com/api/json/v1/1/search.php? s=%s' % name
        response = requests.get(url)
        data = response.json()
        jobs = data['meals']
    return render (request, 'home.html', { "jobs": jobs } )


@login_required
def save(request):
    if request.POST.get('action') == 'post':
        meal = request.POST.get('meal')
        #print(meal)

        meal_dict = ast.literal_eval(meal)
        meal_data = Meal(
        user = request.user,
        name = meal_dict['strMeal'],
        region = meal_dict['strArea']
        )
        meal_data.save()
      

    return render(request, 'home.html') 


def logout(request):
    auth_logout(request)
    return redirect('/login')


def login_page(request):
    return redirect('login')
