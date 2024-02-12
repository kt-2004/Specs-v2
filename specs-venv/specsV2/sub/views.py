from collections import defaultdict
from datetime import datetime
import os
from MySQLdb import IntegrityError as I
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

#This function is made to curbe direct access of pages by the page names.i.e:/feedback etc.
def get_referer(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return None
    return referer
#Terms and conditions function
def terms(request):         
    return render(request,"terms.html")
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
        uEmail = request.POST['uEmail']
        response.set_cookie('username', User.objects.get(uEmail=uEmail).uName)#For getting username also in case of new or updated for name get from the cookie.
        request.session["username"] = User.objects.get(uEmail=uEmail).uName
        uPass = request.POST['uPass']
        print(list(User.objects.all().values_list('uName', flat=True)))#for cmd
        ch=User.objects.get(uEmail=uEmail)
        ch.uPass=uPass
        ch.uName=User.objects.get(uEmail=uEmail).uName
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
    response = redirect("/home/?logout")
    response.set_cookie('username', None)
    response.set_cookie("isLoggedIn", False)
    request.session['username'] = None
    request.session['email'] = None
    return response
#Register and Login function are combined here using User model for both.
def register(request):
    response = redirect("/home/?registered")
    if request.method=='POST':
        if request.POST.get('register', True): #For Register...
            uName=request.POST['uNameR']
            uEmail=request.POST['uEmailR']
            uPass=request.POST['uPassR']
            uPhone=request.POST['uPhoneR']
            formData=User(uName=uName,uEmail=uEmail,uPass=uPass,uPhone=uPhone)
            try:
                formData.save()
            except Exception as e:
                return redirect('/register/?exists')
            response.set_cookie('username',uName)
            request.session['username'] = uName
            print(request.session['username'])
            response.set_cookie('isLoggedIn',True)
            print("user saved" + str(formData))
            return response
        elif request.POST.get('login', True):  #For Login...
            uEmail=request.POST['uEmailL']
            uPass=request.POST['uPassL']
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
#add 3mcqs for each things which is selected by user at runtime.. for accurate result..
@never_cache
def mcq(request):
    if not get_referer(request):
        return redirect("/register")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM sub_student WHERE email='{request.session['email']}'")
        for i in cursor.fetchall():
            if i[-1] != -1: #if score is -1 then you can give xam its a default marks.
                return HttpResponse("<h1>Can't Give Exam Twice.</h1>")  #if score is not -1 then you cannot give xam.
    if request.method == "POST":
        score=0
        subjects = {}   #dictionary
        corrects = {}
        subjects = defaultdict(lambda: 0, subjects)
        corrects = defaultdict(lambda: 0, corrects)
        for i in request.POST.items():
            if "answer_" in i[0]:
                question_id = i[0].replace("answer_","")
                if MCQ.objects.get(id=question_id).correct == i[1].split(")")[0]:   #to check whether the ans is matching with correct ans in the give Que or not.Que id is to identify ques. 
                    score+=1    #add 1marks for each correct answer.
                    subjects[MCQ.objects.get(id=question_id).subject]+=1
                    corrects[MCQ.objects.get(id=question_id).subject]+=1
                else:
                    subjects[MCQ.objects.get(id=question_id).subject]+=1
        print(dict(subjects))   #cmd msg
        print(dict(corrects))   #cmd msg
        request.session["score"]=score  #print score on the browser.
        for i in subjects.keys():
            subjects[i] = str(corrects[i]) + "/" + str(subjects[i])
        request.session["subjects"]=subjects    #here format of score is given i.e Acc=3/3
        print(str(subjects))    #cmd msg
        t = Student.objects.get(email=request.session["email"]) 
        t.result = str(dict(subjects))
        t.score = score
        t.save()
        return redirect("/result")
    temp = []   #empty list for mcqs to be given for test.
    stud = Student.objects.get(email=request.session["email"])  #gets student email from fillform.
    with connection.cursor() as cursor:
        for i in stud.get_interested_subjects_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{i}'")
            t1 = list(cursor.fetchall())    #fetch all ques from user selected int.subs.
            temp+=random.sample(t1,3)       #provide random 3 ques from them.
            t1=[]                           
        for j in stud.get_skills_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{j}'")
            t2 = list(cursor.fetchall())
            print(j,t2)
            temp+=random.sample(t2,3)
            t2=[]
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject1}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject2}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{stud.subject3}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
    questions = []
    for i in temp:
        questions.append([i[0],i[2].replace("Q.",""),i[3],i[4],i[5],i[6]])  #here Q will get replaced by numbers using forloop counter.
    random.shuffle(questions)
    return render(request, 'mcq.html', {'questions':questions})
#To show detail analysis of result or score of user.
@never_cache
def result(request):
    if not get_referer(request):
        return redirect("/register")
    try:
        student = Student.objects.get(email=request.session["email"])
        result = eval(str(student.result)) # eval function is used to represent the score of student.
        response = render(request,"result.html",{"score":student.score,"subjects":result,"info":"Your total score is:"})
        return response
    except:
        return redirect("/myprof")
#Adding csv files of mcq to database here.Get refered function is not required here.
#For-loop is used to add multiple files at once. 
def add_to_db(request):
    # return HttpResponse("check console")
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(r"D:\Specs v2\specs-venv\specsV2\sub\static\\mcq") if isfile(join(r"D:\Specs v2\specs-venv\specsV2\sub\static\\mcq", f))]
    for i in onlyfiles:
        with open(f'sub/static/mcq/{i}', mode ='r',encoding="utf8") as file:
            csvFile = list(csv.reader(file))
            for lines in csvFile:
                if lines != [] and 'Question' not in lines: 
                    try:
                        if MCQ.objects.get(question=lines[0]):  #new condition to check  replicas of csv files.
                            pass
                    except:
                        print(lines)
                        MCQ.objects.create(
                            correct=(lines[5].split(":")[1]).replace(" ",""),
                            question=lines[0],
                            optionA=lines[1],
                            optionB=lines[2],
                            optionC=lines[3],
                            optionD=lines[4],
                            subject=i.replace(".csv","")
                        )
                        continue
    return HttpResponse("check console")
#Function for storing multiple csv of colleges and stream.
def clg_to_db(request):
    # for i in College.objects.all():
    #     print(i.placement)
    #     for j in i.get_streams():
    #         print("Course Name: " + j.name)
    #         print("Fees: " + str(j.fees))
    #         print("Description: " + j.description)
    #         print("Provider College: " + j.college_name.name)
    #         print("\n")
    # return HttpResponse("check console")
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(r"D:\Specs v2\specs-venv\specsV2\sub\static\\Courses") if isfile(join(r"D:\Specs v2\specs-venv\specsV2\sub\static\\Courses", f))]
    n=0
    for i in onlyfiles:
        with open(f'sub/static/Courses/{i}', mode ='r',encoding="utf8") as file:
            csvFile = list(csv.reader(file))
            for lines in csvFile:
                if len(lines) != 0:
                    if lines[0] == "Name":
                        continue
                    try:
                        if College.objects.get(name=lines[0]):
                            # print("College exists: " + lines[0])
                            pass
                    except:
                        College.objects.create(
                                name=lines[0],
                                address=lines[1],
                                placement=lines[3],
                                hostel=lines[4],
                                transport=lines[5],
                                link=lines[6]
                            )
                    clg = College.objects.get(name=lines[0])
                    try:
                        if Stream.objects.get(name=i.replace(".csv",""),college_name=clg):
                            # print("Course for college already exists")
                            continue
                    except:
                        Stream.objects.create(
                            name=i.replace(".csv",""),
                            fees=lines[2],
                            college_name = clg
                            )
                        n=n+1
                        print(f"Made stream {i.replace('.csv','')}:" + str(n))
                        for j in Stream.objects.filter(college_name=clg):
                            clg.courses.add(j.id)
                        clg.save()
    return HttpResponse("check console")

