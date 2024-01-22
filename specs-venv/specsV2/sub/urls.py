from django.contrib import admin
from django.urls import path
from sub import admin
from sub import views
urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.home, name=''),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('feedback/',views.feedback,name='feedback'),
    path('forgotpass/',views.forgotpass,name='forgotpass'),
    path('changepass/',views.changepass,name='changepass'),
    path('myprof/',views.myprof,name='myprof'),
    path('register/',views.register,name='register'),
    path('logout/',views.logout,name='logout'),
    path('fillform/',views.fillform,name='fillform'),
    path('mcq/',views.mcq,name='mcq'),
    path('add/',views.add_to_db,name='add'),
    path('clg/',views.clg_to_db,name='clg'),
    path('result/',views.result,name='result'),

]    