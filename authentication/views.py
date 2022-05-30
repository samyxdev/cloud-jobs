from django.shortcuts import render , redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse
from django.shortcuts import render

import requests
import ast
import logging
import uuid

from .models import Jobs, CV


logger = logging.getLogger(__name__)

def index(request):
    jobs = Jobs()
    context = {"jobs":jobs.get_jobs()}

    return render(request, 'index.html', context)

def search(request):
    if request.method == 'GET':
        filters = {}
        filters[":title"] = request.GET.get("title")
        filters[":skills"] = request.GET.get("skills").strip(" ").split(",")

        if filters[":title"] == "" and filters[":skills"][0] == '':
            filters = None

        print(filters)

        jobs = Jobs()
        context = {"jobs":jobs.get_jobs(filters=filters)}

        print(filters)

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

@login_required
def upload(request):
    # If we are comming after an upload
    if request.method == 'POST' and request.FILES['file']:
        logger.info("Upload page: Uploaded a CV...")
        user_file = request.FILES["file"]

        cv = CV()
        skills = cv.handle_cv_upload(user_file, str(uuid.uuid4()), request.user.username)
        return upload_with_skills(request, skills)
    else:
        # If we can find skills related to that user in the db, we'll print them
        cv = CV()
        skills = cv.get_user_skills(request.user.username)
        if not skills is None:
            logger.info("Upload page: Existing skills")
            return upload_with_skills(request, skills)

        # Rendering without jobs as no skills were found
        else:
            logger.info("Upload page: No existing skills")
            return render(request, 'upload.html', context={"jobs":[], "skills":[]})

        #return render(request, 'upload.html')


@login_required
def upload_with_skills(request, skills):
    """Called by upload when an user already uploaded a CV.
    Displays jobs from the DB using the user's skills"""

    context = {"skills":skills, "jobs":[]}

    jobs = Jobs()
    context["jobs"] = jobs.get_jobs(filters={":title":"", ":skills":skills})

    return render(request, 'upload.html', context=context)

def profile(request):
    jobs = Jobs()
    context = {"jobs":jobs.get_saved_jobs(request.user.username)}

    return render(request, 'profile.html', context)

@login_required
def save(request):
    if request.POST.get('action') == 'post':
        job_fields = request.POST.get('job')
        #job_fields = request.POST['job']
        job_dict = ast.literal_eval(job_fields)
        job = Jobs()
        #if job.check_saved_jobs(request.user.username, job_dict['link']):
        #pass
        #else:
        status = job.save_job(request.user.username, job_dict['link'], job_dict['title'], job_dict['company'], job_dict['description'], job_dict['skills'], job_dict['location'], job_dict['salary'] )
        return HttpResponse('', status=status)


def logout(request):
    auth_logout(request)
    return redirect('/login')


def login_page(request):
    return redirect('login')


#def get_saved_jobs(request):
#    jobs = Jobs()
#    context = {"jobs":jobs.get_saved_jobs(request.user)}
#    return render(request, 'profile.html', context)
