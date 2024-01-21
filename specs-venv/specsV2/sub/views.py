from collections import defaultdict
from datetime import datetime
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
from django.core.mail import EmailMessage
import random
import csv
from django.db import connection
from django.views.decorators.cache import never_cache

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
    changepass=redirect("/forgotpass?otp")# To get user on otp page.
    if not get_referer(request):
        return redirect("/register")
    if request.method == 'POST':
        if not request.POST['OTP']:
            email=request.POST.get('email')
            print(email)
            changepass.set_cookie("otp", SendEmail(email,request))
            return changepass
        else:
            otp = request.POST.get("OTP")
            if otp == request.COOKIES.get("otp"):#Compares otp got from user and stored in the cookie.
                return redirect("changepass")
            else:
                return HttpResponse("<h1>Incorrect OTP.</h1>") #Msg
    return render(request,"forgotpass.html")
def changepass(request):
    if not get_referer(request):
        return redirect("/register")
    if request.method=="POST":
        response=redirect("/?password_changed")#After changing password gets user to home page.
        uName = request.POST['uName']
        response.set_cookie('username',uName)#For getting username also in case of new or updated for name get from the cookie.
        request.session["username"] = uName
        uPass = request.POST['uPass']
        print(list(User.objects.all().values_list('uName', flat=True)))#for cmd
        ch=User.objects.get(uName=uName)
        ch.uPass=uPass
        ch.uName=uName 
        ch.save()
        return response
    else:
        return render(request,"changepass.html")
#Myprofile with score of students and also can update username.
def myprof(request):
    if not get_referer(request):
        return redirect("/register")
    if request.method=="POST":
        uEmail = request.POST['uEmail']
        uName = request.POST['uName']
        uPhone = request.POST['uPhone']
        prof=User.objects.get(uName=request.session['username'])
        prof.uEmail=uEmail       #Stores updated or new email here.
        prof.uName=uName       #Stores updated or new username here.
        prof.uPhone=uPhone       #Stores updated or new phone here.
        prof.save()
        #To get updated things on the same pages again.or after refresh.
        response = render(request,"myprof.html",{'uName':uName,'uEmail':uEmail,'uPhone':uPhone})
        response.set_cookie('username',prof.uName) #To get updated user name its stored in the cookie.
        return response
    if request.session.get("username","") != "":
        try:
            prof=User.objects.get(uName=request.session['username'])
            print(prof.uName)
            try:
                student = Student.objects.get(email=request.session["email"])
                result = eval(str(student.result)) # eval function is used to represent the score of student .
                response = render(request,"myprof.html",{'uName':prof.uName,'uEmail':prof.uEmail,'uPhone':prof.uPhone,"score":student.score,"subjects":result,"info":"Your total score is:"})
                return response
            except:
                response = render(request,"myprof.html",{'uName':prof.uName,'uEmail':prof.uEmail,'uPhone':prof.uPhone})
                return response
        except Exception as e:
            print("Exception!!!!!!") #for cmd
            return HttpResponse("500 Internal server error")
    else:
        return redirect("/register")
#Logout...
def logout(request):
    response = render(request,"index.html")
    response.set_cookie('username', None)
    response.set_cookie("isLoggedIn", False)
    request.session['username'] = None
    request.session['email'] = None
    return response
#Register and Login function are combined here using User model for both.
def register(request):
    response = redirect("home")
    if request.method=='POST':
        if request.POST.get('register', False): #For Register...
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
        elif request.POST.get('login', False):  #For Login...
            uEmail=request.POST['uEmail']
            uPass=request.POST['uPass']
            try:
                user=User.objects.get(uEmail=uEmail)
            except:
                return render(request,"register.html",{"error":"Incorrect Email or password"})
            if user.uPass == uPass:
                response.set_cookie('username', user.uName)
                response.set_cookie('isLoggedIn',True)
                request.session['username'] = User.objects.get(uEmail=uEmail).uName
                print(request.session['username'])
                return response
            else:
                return render(request,"register.html",{"error":"Incorrect Email or password"})
    return render(request,"register.html")
#Feedback...
def feedback(request):
    if not get_referer(request):
        return redirect("/register")
    if request.method == "POST":
        print("getting feedback")#for cmd
        submitter = User.objects.get(uName=request.session["username"])
        feedback = request.POST['feedback']
        Feedback.objects.create(submitter=submitter, feedback=feedback)
    return render(request,"feedback.html")
#Email is send to who is give in this def.
def SendEmail(email,request):
    otp = str(random.randint(1000, 9999))
    email = EmailMessage('OTP', otp ,to=[email])
    email.send()
    return otp
#Form for students details for forming questions based on thier choices.
def fillform(request):
    if not get_referer(request):
        print("user not logged in") #for cmd
        return redirect("/register")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM sub_student WHERE email='{request.session['email']}'")
        print(cursor.fetchall())
        for i in cursor.fetchall():
            if i[-1] != -1:
                return HttpResponse("<h1>Can't Give Exam Twice.</h1>")
    isLoggedIn = request.COOKIES.get('isLoggedIn','False')
    if isLoggedIn=='True':
        if request.method == 'POST':
            try:
                Student.objects.get(email=request.POST["email"])#For using one email at time.
                return HttpResponse("Email Already Exists")#Msg
            except:
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
                    marks3 = int(request.POST["marks3"]),
                    skills = ((str(request.POST.getlist("skills[]")).replace("[","")).replace("]","")).replace("\'",""),
                    interested_subjects = ((str(request.POST.getlist("interested_subjects[]"))).replace('[', '')).replace(']', '').replace("\'",""),
                    score=-1
                )
                request.session["email"] = request.POST["email"]
                return redirect("/mcq")
        else:
            print("No form found") #for cmd
    else:
        return redirect("/register")
    return render(request,"fillform.html")
#MCQ are filtered here n modified.
@never_cache
def mcq(request):
    if not get_referer(request):
        return redirect("/register")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM sub_student WHERE email='{request.session['email']}'")
        for i in cursor.fetchall():
            print(i[-1])
            if i[-1] > -1:
                return HttpResponse("<h1>Can't Give Exam Twice.</h1>")
    if request.method == "POST":
        score=0
        subjects = {}
        corrects = {}
        subjects = defaultdict(lambda: 0, subjects)
        corrects = defaultdict(lambda: 0, corrects)
        for i in request.POST.items():
            if "answer_" in i[0]:
                question_id = i[0].replace("answer_","")
                if MCQ.objects.get(id=question_id).correct == i[1].split(")")[0]:
                    score+=1
                    subjects[MCQ.objects.get(id=question_id).subject]+=1
                    corrects[MCQ.objects.get(id=question_id).subject]+=1
                else:
                    subjects[MCQ.objects.get(id=question_id).subject]+=1
        print(dict(subjects))
        print(dict(corrects))
        request.session["score"]=score
        for i in subjects.keys():
            subjects[i] = str(corrects[i]) + "/" + str(subjects[i])
        request.session["subjects"]=subjects
        print(str(subjects))
        t = Student.objects.get(email=request.session["email"])
        t.result = str(dict(subjects))
        t.score = score
        t.save()
        return redirect("/result")
    temp = []
    stud = Student.objects.get(email=request.session["email"])
    with connection.cursor() as cursor:
        for i in stud.get_interested_subjects_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{i}'")
            temp += list(cursor.fetchall())
        for i in stud.get_skills_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{i}'")
            temp += list(cursor.fetchall())
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject1}'")
        temp += list(cursor.fetchall())
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject2}'")
        temp += list(cursor.fetchall())
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject3}'")
        temp += list(cursor.fetchall())
    formatted_temp = []
    for i in temp:
        formatted_temp.append([i[1],i[2],i[3],i[4],i[5],i[0]])
    questions = random.sample(formatted_temp,15)
    return render(request, 'mcq.html', {'questions':questions})

@never_cache
def result(request):
    try:
        student = Student.objects.get(email=request.session["email"])
        result = eval(str(student.result)) # eval function is used to represent the score of student.
        response = render(request,"result.html",{"score":student.score,"subjects":result,"info":"Your total score is:"})
        return response
    except:
        return redirect("/myprof")
#Adding csv files of mcq to database here.Get refered function is not required here.
def add_to_db(request):
    for i in College.objects.all():
        print(i.name + str(i.get_streams(id=i.id)))
    return HttpResponse("check console")
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(r"D:\Specs v2\specs-venv\specsV2\sub\static") if isfile(join(r"D:\Specs v2\specs-venv\specsV2\sub\static", f))]
    for i in onlyfiles:
        with open(f'sub/static/{i}', mode ='r',encoding="utf8") as file:
            csvFile = list(csv.reader(file))
            for lines in csvFile:
                if lines != []: 
                    print((lines[5]))
                    try:
                        MCQ.objects.create(
                            correct=(lines[5].split(":")[1]).replace(" ",""),
                            question=lines[0],
                            optionA=lines[1],
                            optionB=lines[2],
                            optionC=lines[3],
                            optionD=lines[4],
                            subject=i.replace(".csv","")
                        )
                    except:
                        continue
    return HttpResponse("check console")