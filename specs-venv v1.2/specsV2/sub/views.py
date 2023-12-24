from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
from django.core.mail import EmailMessage
import random

# Create your views here.

def get_referer(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return None
    return referer
def home(request):
    return render(request,"index.html")
def about(request):
    return render(request,"about.html")
def contact(request):
    if request.method == "POST":
        cName = request.POST.get("cName")
        cEmail = request.POST.get("cEmail")
        cPhone = request.POST.get("cPhone")
        cMsg = request.POST.get("cMsg")
        Contact.objects.create(cName=cName, cEmail=cEmail, cPhone=cPhone, cMsg=cMsg)
        return redirect("home")
    return render(request,"contact.html")
@csrf_exempt
def forgotpass(request):
    changepass=redirect("/forgotpass?otp")
    if not get_referer(request):
        return HttpResponse("<h1>Please Login first.</h1>")
    if request.method == 'POST':
        if not request.POST['OTP']:
            email=request.POST.get('email')
            print(email)
            changepass.set_cookie("otp", SendEmail(email,request))
            return changepass
        else:
            otp = request.POST.get("OTP")
            if otp == request.COOKIES.get("otp"):
                return redirect("changepass")
            else:
                return HttpResponse("Incorrect OTP")
    return render(request,"forgotpass.html")
def changepass(request):
    if not get_referer(request):
        return HttpResponse("<h1>Please Login first.</h1>")
    if request.method=="POST":
        response=redirect("/?password_changed")
        uName = request.POST['uName']
        response.set_cookie('username',uName)
        request.session["username"] = uName
        uPass = request.POST['uPass']
        print(list(User.objects.all().values_list('uName', flat=True)) 
)
        ch=User.objects.get(uName=uName)
        ch.uPass=uPass
        ch.uName=uName 
        ch.save()
        return response
    else:
        return render(request,"changepass.html")
def myprof(request):
    if not get_referer(request):
        return HttpResponse("<h1>Please Login first.</h1>")
    if request.method=="POST":
        uEmail = request.POST['uEmail']
        uName = request.POST['uName']
        uPhone = request.POST['uPhone']
        prof=User.objects.get(uName=request.session['username'])
        prof.uEmail=uEmail
        prof.uName=uName
        prof.uPhone=uPhone
        prof.save()
        response = render(request,"myprof.html",{'uName':uName,'uEmail':uEmail,'uPhone':uPhone})
        response.set_cookie('username',prof.uName)
        return response
    if request.session.get("username","") != "":
        try:
            prof=User.objects.get(uName=request.session['username'])
            print(prof.uName)
            response = render(request,"myprof.html",{'uName':prof.uName,'uEmail':prof.uEmail,'uPhone':prof.uPhone})
            return response  
        except Exception as e:
            print(e)
    else:
        print("No user found in session")
def logout(request):
    response = render(request,"index.html")
    response.set_cookie('username', None)
    response.set_cookie("isLoggedIn", False)
    request.session['username'] = None
    return response
def register(request):
    response = redirect("home")
    if request.method=='POST':
        if request.POST.get('register', False):
            uName=request.POST['uName']
            uEmail=request.POST['uEmail']
            uPass=request.POST['uPass']
            uPhone=request.POST['uPhone']
            formData=User(uName=uName,uEmail=uEmail,uPass=uPass,uPhone=uPhone)
            formData.save()
            response.set_cookie('username',uName)
            request.session['username'] = uName
            print(request.session['username'])
            response.set_cookie('isLoggedIn',True)
            print("user saved" + str(formData))
            return response
        elif request.POST.get('login', False):
            uEmail=request.POST['uEmail']
            uPass=request.POST['uPass']
            user=User.objects.get(uEmail=uEmail)
            if user.uPass == uPass:
                response.set_cookie('username', user.uName)
                response.set_cookie('isLoggedIn',True)
                request.session['username'] = User.objects.get(uEmail=uEmail).uName
                print(request.session['username'])
                return response
    return render(request,"register.html")
def feedback(request):
    if not get_referer(request):
        return HttpResponse("<h1>Please Login first.</h1>")
    if request.method == "POST":
        print("getting feedback")
        submitter = User.objects.get(uName=request.session["username"])
        feedback = request.POST['feedback']
        Feedback.objects.create(submitter=submitter, feedback=feedback)
    return render(request,"feedback.html")
def SendEmail(email,request):
    otp = str(random.randint(1000, 9999))
    email = EmailMessage('OTP', otp ,to=[email])
    email.send()
    return otp
def fillform(request):
    if not get_referer(request):
        return HttpResponse("<h1>Please Login first.</h1>")
    if request.method == 'POST':
        print(request.POST.getlist("subject[]")[0])
        Student.objects.create(
            first_name = request.POST["first_name"],
            last_name = request.POST["last_name"],
            date_of_birth = datetime.strptime(request.POST["date_of_birth"], '%Y-%m-%d').date(),
            email = request.POST["email"],
            seat_no = request.POST["seat_no"],
            stream = request.POST["stream"],
            subject1 = request.POST.getlist("subject[]")[0],
            subject2 = request.POST.getlist("subject[]")[1],
            subject3 = request.POST.getlist("subject[]")[2],
            marks1 = int(request.POST["marks1"]),
            marks2 = int(request.POST["marks2"]),
            marks3 = int(request.POST["marks3"])
        )
        return HttpResponse("Form submitted successfully!")
    else:
        print("No form found")
    return render(request,"fillform.html")