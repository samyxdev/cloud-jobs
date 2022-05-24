from django.urls import path
from . import views
from django.urls import re_path
from django.conf import settings

urlpatterns = [
    path('', views.index , name='index'),
    path('register', views.register, name='register' ),
    path('home',views.home , name= 'home'),
    path('cv', views.cv, name='cv' ),
    re_path(r'^logout/$', views.logout, name='logout'),
    path('savejob', views.save, name='savejob')
    
]
