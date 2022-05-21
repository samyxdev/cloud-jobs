from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from .forms import JobDescriptionForm


# Create your views here.
def index(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password =password)

        if user is not None:
            auth.login(request , user)
            return redirect('/home')    
        else:
            messages.info(request, 'invalid username or password')
            return redirect("/")
    else:
        return render(request,'index.html')


def register(request):

    if request.method == 'POST':

        email = request.POST['email']
        username = request.POST['username']
        password= request.POST['password']


        user = User.objects.create_user(username = username , password = password , email = email)
        user.save()
        print('user created')
        return redirect('/custom')

    return render(request,'register.html')


@login_required
def home(request):    
    form = JobDescriptionForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
             job_description = form.save(commit=False)
             job_description.user = request.user
             job_description.save()
             return redirect('.')
        else:
             print('No tuple addded in the database')

    context_dict = {'form': form}
    return render(request, 'home.html', context_dict)


def logout(request):
    auth_logout(request)
    return redirect('/')
