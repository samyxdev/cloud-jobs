from django.urls import path
from . import views
from django.urls import re_path
from django.conf import settings

urlpatterns = [
    path('', views.index , name='index'),
    path('login', views.login , name='login'),
    path('register', views.register, name='register'),
    re_path(r'^logout/$', views.logout, name='logout'),
    path('savejob', views.save, name='savejob'),
    path('upload', views.upload, name='upload'),
    path('profile', views.profile, name='profile'),
    path('login_page', views.login_page, name='login_page'),
    path('search', views.search, name='search')
]
