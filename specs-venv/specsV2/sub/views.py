from collections import defaultdict
from datetime import datetime
import math
import os
from MySQLdb import IntegrityError as I
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.decorators.csrf import csrf_exempt
from .models import *
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
                response = render(request,"myprof.html",{'uName':prof.uName,'uEmail':prof.uEmail,'uPhone':prof.uPhone,"score":student.score,"subjects":result,"info":"Your total score is:","percentage":round(student.score*100/27,2)})
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
    if 'questions' in list(request.session.keys()):
        del request.session['questions'] # if you cmmt this line then only you'll be able to logout.
    request.session.modified = True
    return response
#Register and Login function are combined here using User model for both.
def register(request):
    response = redirect("/home/?registered")
    if request.method=='POST':
        print(list(request.POST.keys()))
        if 'register' in list(request.POST.keys()): #For Register...
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
            request.session['email'] = uEmail
            print(request.session['username'])
            response.set_cookie('isLoggedIn',True)
            print("user saved" + str(formData))

            return response
        elif 'login' in list(request.POST.keys()): #For Login...
            print("logging in...")
            uEmailL=request.POST['uEmailL']
            uPassL=request.POST['uPassL']
            try:
                print(uEmailL)
                user=User.objects.get(uEmail=uEmailL)
            except Exception as e:
                print(e)
                return render(request,"register.html",{"error":"Incorrect Email or password"})
            if user.uPass == uPassL:
                response.set_cookie('username', user.uName)
                response.set_cookie('isLoggedIn',True)
                request.session['username'] = user.uName
                request.session['email'] = user.uEmail
                print(request.session['username'])
                return response
            else:
                return render(request,"register.html",{"error":"Incorrect Email or password"})
        else:
            print("invalid url data")
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
    print(request.session['username'])
    if request.session['username'] == None:
        return redirect("/register")
    if int(User.objects.get(uEmail=request.session["email"]).Student.score) != -1:
        return HttpResponse("<h1>Can't Give Exam Twice.</h1>")
    isLoggedIn = request.COOKIES.get('isLoggedIn','False')
    if isLoggedIn=='True':
        if request.method == 'POST':
            Student.objects.create(
                    first_name = request.POST["first_name"],
                    last_name = request.POST["last_name"],
                    date_of_birth = datetime.strptime(request.POST["date_of_birth"], '%Y-%m-%d').date(),
                    email = request.session["email"],
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
            usr = User.objects.get(uEmail=request.session["email"])
            usr.Student = Student.objects.get(email=request.session["email"])
            usr.save()
            print(User.objects.get(uEmail=request.session["email"]).Student)
            print(Student.objects.get(email=request.session["email"]))
            return redirect("/mcq")
        else:
            print("No form found") #for cmd
    else:
        return redirect("/register")
    print(request.session["email"])
    return render(request,"fillform.html",{"e_mail":request.session["email"]})
#MCQ are filtered here n modified.
#add 3mcqs for each things which is selected by user at runtime.. for accurate result..
@never_cache
def mcq(request):
    if not get_referer(request):
        return redirect("/register")
    if int(User.objects.get(uEmail=request.session["email"]).Student.score) != -1:
        return HttpResponse("<h1>Can't Give Exam Twice.</h1>")  #if score is not -1 then you cannot give xam.
    if request.method == 'POST':#updated
        pass
    elif 'questions' in list(request.session.keys()):#updated
        return render(request, 'mcq.html', {'questions':request.session['questions']})
    if request.method == "POST":
        print("showing result...")
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
        request.session["score"]=score  #print score on the browser.
        for i in subjects.keys():
            subjects[i] = str(corrects[i]) + "/" + str(subjects[i])
        request.session["subjects"]=subjects    #here format of score is given i.e Acc=3/3
        t = User.objects.get(uEmail=request.session["email"]).Student
        t.result = str(dict(subjects))
        t.score = score
        t.save()
        return redirect("/result")
    temp = []   #empty list for mcqs to be given for test.
    student_obj = User.objects.get(uEmail=request.session["email"]).Student  #gets student email from fillform.
    print(len(student_obj.get_interested_subjects_list()))
    print(len(student_obj.get_skills_list()))
    with connection.cursor() as cursor:
        for i in student_obj.get_interested_subjects_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{i}'")
            t1 = list(cursor.fetchall())    #fetch all ques from user selected int.subs.
            print(i,t1)
            temp+=random.sample(t1,3)       #provide random 3 ques from them.
            t1=[]                  
        for j in student_obj.get_skills_list():
            cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{j}'")
            t2 = list(cursor.fetchall())
            print(j,t2)
            temp+=random.sample(t2,3)
            t2=[]
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{student_obj.subject1}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{student_obj.subject2}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
        cursor.execute(f"SELECT * FROM sub_MCQ WHERE subject='{student_obj.subject3}'")
        temp +=  random.sample(list(cursor.fetchall()),3)
    questions = []
    for i in temp:
        questions.append([i[0],i[2].replace("Q.",""),i[3],i[4],i[5],i[6]])  #here Q will get replaced by numbers using forloop counter.
    random.shuffle(questions)
    request.session['questions']=questions 
    return render(request, 'mcq.html', {'questions':questions})
#To show detail analysis of result or score of user.
def result(request):
    if not get_referer(request):
        return redirect("/register")
    try:
        student = User.objects.get(uEmail=request.session["email"]).Student
        result = eval(str(student.result)) # eval function is used to represent the score of student.
        response = render(request,"result.html",{"score":student.score,"subjects":result,"info":"Your total score is:","percentage":round(student.score*100/27,2)})
        return response
    except Exception as e:
        print(e)
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

def stream_desc(request):
    strup = """1. BCA
Sub:Computer,English,Mathematics,Logical and Reasoning,Statistics,Ethical Hacking,Web Design,Computer Architecture,Cyber Security,Coding,Digital Arts,Leadership,Research and Obervation,Robotics & ML/AI,Animation

2. BAF
Sub:Mathematics, Accounts,Business Adminstration,English,Computer,Satistics,Civics,Trigonometry,Writing,Leadership,Law

3. Company Secretary
Sub:Accounts,Economics,Business Administration,English,Arithmetic,Algebra,Civics,Law,Statistics,Leadership,Management

4. Cost and Management Accountant
Sub:Mathematics, Account,Economics,Business Administration,English,Computer,Arithmetic,Algebra,Statistics,Reading,Writing,Management,Leadership

5. Bachelor of Economics 
Sub: Statistics, Mathematics, Economics,English,Accounts,Satistics,Civics,Political Science,Research and observation,Leadership  

6. BCOM
Sub:Mathematics, Account,Economics,Business Administration,English,Computer,Statistics,Arithmetic,Leadership,Logical and Reasoning

7. BBA
Sub: Business Administration, Accounts,Computer,English,Statistics,Economics,Law,Web Design,Leadership,Logical and Reasoning,Research and observation

8. Bachelor of Business Management
Sub:Accounts, Business Administration, Economics, English,Mathematics,Staistics,Arithmetic,Algebra,Law,Civics,Leadership,Computer,Digital Arts

9. Integrated MBA 
Sub: Accounts, Business Administration, Economics, English,Computer,Law,Civics,Logical and Reasoning,Leadership,Management,Research and Observation

10. LLB 
Sub:English,Mathematics,History,Civics,Political Science,Economics,Law,Economics,Psychology,Statistics,Management,Leadership,Reading,Writing,Anchoring

12. BSc IT
Sub:English,Mathematics,Statistics,Computer,Computer Architecture,Web Design,Ethical Hacking,Cyber Security,Robotics & ML/AI,Coding,Digital Arts,Leadership,Research and Observation

14. Media and Communication
Sub: Sociology, English, Mathematics,Economics,Business Administration,Political Science,Law,Civics,Digital Arts,Philosophy,Leadership,Management,Reading,Writing,Anchoring,Animation

15. Mass and Communication 
Sub:English,Sociology,Political Science,Civics,Fine Arts,Digital Arts,Photography,Geography,Travelling,Leadership,Anchoring,Animation,Reading,Writing,Leadership

16. Mass and Communication in Film
Sub:English, Histroy,Gujarati,Fine Arts,Digital Arts,Photography,Geography,Travelling,Leadership,Anchoring,Animation,Reading,Writing,Acting,Makeup,Music,Leadership,P.T,Computer

17. BSc in Biology
sub:Biology,Chemistry,Physics,Mathematics,Statistics,Reading,Writing,Computer,Management,English,Lab Skills,Research and Observation

18. BSc in Microbiology
sub:Biology,English,Chemistry,Physics,Mathematics,Computer,Statistics,Psychology,Management,Leadership

19. Bachelor in Dental surgery
sub:Biology,English,Chemistry,Physics,Mathematics,Computer,Statistics,Psychology,Management,Leadership

20. BSc in zoology
sub:Biology,English,Chemistry,Leadership,Geography,Wildlife Research,History,Lab Skills,Research and Observation,Travelling,Environmental Science

21. BSc in Medical Technology
sub:Biology,Mathematics,Physics,Chemistry,English,Coding,Leadership,Environmental Science,Robotics & ML/AI,Computer Architecture

22. BSc in Biotechnology
sub:Biology,Chemistry,Mathematics,English,Coding,Cyber Security,Lab Skills,Research and Observation,Logical and Reasoning,Computer Architecture

23. BSc in Botany
sub:Biology,Chemistry,Mathematics,English,Gardening,Environmental Science,Lab Skills,Research and Observation,Leadership,Travelling,

24. Bachelor of Homeopathic Medicine and Surgery
sub:Biology,Chemistry,Mathematics,English,Sanskrit,P.T,Lab Skills,Gardening,Environmental Science, Cooking,History

25. BSc in Nursing
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Travelling,Leadership,

26. BSc in Life Science
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Environmental Science,Wildlife Research,Gardening,Leadership,Reading

27. MBBS
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Logical and Reasoning,Reading,Writing,Leadership,Psychology

28. Bachelor of Veterinary Sciences
sub:Biology,Chemistry,Physics,English,Environmental Science,Wildlife Research,Lab Skill,Research and Observation,

29. Bachelor of Pharmacy
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Reading,Writing,Civics,Mathematics,Computer

30. BSc in Food Technology
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Physics,Computer,Electronics and Hardware,Cooking,Photography,P.T

31. BSc in Agriculture
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,P.T,Environmental Science,Gardening,Carpentry,Wildlife Research,Electronics and Hardware

32. BSc in Genetics
sub:Biology,Chemistry,Physics,Mathematics,English,Lab Skills,Research and Observation,Computer,Statistics,Trigonometry,Logical and Reasoning

33. Bachelor of Science in Agrochemical Science
sub:Biology,Chemistry,Physics,Mathematics,English,Lab Skills,Research and Observation,Geography,Electronics and Hardware,Environmental Science,Leadership

34. Bachelor of Ayurvedic Medicine and Surgery
sub:Biology,Chemistry,Physics,Sanskrit,English,Environmental Science,P.T,Lab Skills,Gardening, Cooking,History,Leadership,Music

35. BSc in Dairy Farming
sub:Biology,Chemistry,Physics,English,Environmental Science,P.T,Lab Skills,Wildlife Research,Geography,Geometry,Leadership,Photography,Writing

36. B.Tech in Dairy Technology
sub:Biology,Chemistry,Physics,English,Environmental Science,P.T,Lab Skills,Wildlife Research,Geography,Geometry,Leadership,Photography,Writing,Computer,Computer Architecture

37. BSc in Audiology
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Computer

38. Bachelor in Optometry
sub:Biology,Chemistry,Physics,English,Mathematics,P.T,Lab Skills,Research and Observation,Management,Computer

39. Diploma in Pharmacy
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Reading,Writing,Civics,Mathematics,Computer

40. Diploma in Nursing
sub:Biology,Chemistry,Physics,English,Lab Skills,Research and Observation,Travelling,Leadership

41. Diploma in Medical Laboratory Technology
sub:Biology,Chemistry,Physics,English,Mathematics,Computer,Lab Skills,Research and Observation,Management

43. Diploma in Operation Theatre Technology
sub:Biology,Chemistry,Physics,English,Mathematics,Computer,Lab Skills,Research and Observation,Management

44. Diploma in X-Ray technology
sub:Biology,Chemistry,Physics,English,Mathematics,Computer,Lab Skills,Research and Observation,Management,Electronics and Hardware 

45. Bachelor in Physiotherapy
sub:Biology,Chemistry,Physics,English,Mathematics,P.T,Lab Skills,Research and Observation,Management,Outdoor Games,Indoor Games

46. Diploma in Nutrition and Dietetics
sub:Biology,Chemistry,Physics,English,P.T,Cooking,Writing,Indoor Games,Outdoor Games,Logical and Reasoning,Lab Skills,Research and Observation,Management

47. B.Tech in Computer Science and Engineering
sub:Computer, Mathematics,Physics,Chemistry,English ,Coding,Computer Architecture,Web Design,Logical and Reasoning,Cyber Security,Electronics or Hardware,Reading

48. B.Tech in Mechanical Engineering
sub:Mathematics,Physics,Chemistry,Computer,Economics,Statistics,Electronics and Hardware ,Logical and Reasoning, Geometry,History,Leadership,Management,Outdoor Games,Research and Observations

49. B.Tech in Electrical Engineering
Sub:Electronics and Hardware,Mathematics,Physics,Chemistry,Arithmetic,Algebra,Geometry,Computer Architecture,Logical and Reasoning,Trigonometry,Coding ,Digital Arts,Management,Leadership 

50. B.Tech in Civil Engineering
sub:Mathematics,Physics,Chemistry,Computer,English,P.T,Coding ,Logical and Reasoning ,Management ,Leadership,Outdoor Games,Geometry

51. B.Tech in Chemical Engineering
sub:Chemistry,Physics,Mathematics,English,Computer,Cyber Security,Coding,Logical and Reasoning,Leadership

52. BA in Biology
sub:Biology,Physics,Chemistry,English,Reading,Writing,Logical and Reasoning,Lab Skills,Environmental Science,Research and Observation

53. BA in Communication
sub:English,Sociology,Psychology,Leadership,Anchoring,Writing,Reading,Law,Digital Arts,Research and Observation

54. BA in Economics
sub:Economics,Mathematics,Political Science,Satistics,Writing,Business Adminstration,English,Law,Civics,Anchoring,History,Logical and Reasoning

55. BA in Education
sub:English,Psychology,Sociology,Mathematics,Writing,Reading,Leadership,History,Environmental Science,Anchoring,Research and Observation,Painting,Digital Arts

56. BA in English
sub:English,History,Writing,Reading,Painting,Sociology,Philosophy

57. BA in History
sub:History,Political Science,Sociology,Economics,Reading,Writing,English,Research and Observation,Leadership,Anchoring

58. BA in Journalism
sub:English,Gujarati,Political Science,Sociology,Economics,History,Leadership,Anchoring,Animation,Travelling,Law,Geography,Reading,Writing,Research and Observation,Logical and Reasoning

59. BA in Philosophy
sub:English,History,Sociology,Political Science,Economics,Sanskrit,Psychology,Logical and Reasoning,Reading,Writing,Leadership,Philosophy,Travelling

60. BA in Political Science
sub:English,Gujarati,Political Science,Psychology,Economics,Leadership,Writing,Anchoring,Law,Research and Observation,Logical and Reasoning

61. BA in Psychology
sub:Psychology,Biology,Satistics,Sociology,English,Gujarati,Sanskrit,Management,Research and Observation,Reading,Leadership

62. BA in Studio Art
sub:History,Sociology,English,Fine Arts,Digital Arts,Photography,Management,Painting,Handicrafts and Arts,Knitting,Carpentery

63. BA in Theatre and Drama
sub:English,Gujarati,Sanskrit,Sociology,Fine Arts,Acting,Music,Leadership,Travelling,Psychology

64. BA in Music
sub:English,Gujarati,Sanskrit,Psychology,Fine Arts,Digital Arts,Photography,Music,Management,

65. BDes in fashion Designing
sub:English,History,Fine Arts,Digital Arts,Photography,Handicraft and Arts,Management,Painting,

66. BDes in Interior Design
sub:Mathematics,Physics,Geography,English,Fine Arts,Digital Arts,Psychology,Painting,Management,Animation

67. BDes in Communication Design
sub:Mathematics,English,History,Computer,Digital Arts,Fine Arts,Writing,Law,Research and Observation

68. BDes in Industrial & Product Design
sub:Mathematics,Physics,English,Physics,Chemistry,Fine Arts,Digital Arts,Business Administration,Management,Law,Research and Observation

69. Bachelor of Journalism & Mass Communication
sub:English,Gujarati,Political Science,Sociology,Economics,History,Leadership,Anchoring,Animation,Travelling,Law,Geography,Reading,Writing,Research and Observation,Logical and Reasoning

70. BA LLB
sub:Mathematics,Economics,Political Science,History,English,Logical and Reasoning,Leadership,Management,Anchoring,Psychology,Law,Reading,Writing

71. Diploma in Education
sub:English,Psychology,Sociology,Mathematics,Writing,Reading,Leadership,History, Environmental Science,Anchoring,Research and Observation,Painting,Digital Arts

72. BBA Hons in Hospitality and Tourism Management
Sub:English,Economics,Business Administration,Accounts,Fine Arts,Leadership,Management,Travelling,Geography

73. Diploma in 3D Animation
Sub:English,Computer,Mathematics,Algebra,Geometry,Trigometry,Digital Arts,Animation,Painting

74. Advanced Diploma in Animation
Sub:English,Computer,Mathematics,Algebra,Geometry,Trigometry,Digital Arts,Animation,Painting

75. Diploma in Aviation Management
Sub:Mathematics,English,Computer,Geography,Environmental Science,Travelling,Leadership,Management,Makeup

76. Diploma in Beauty Therapy
Sub:Biology,English,P.T,Psychology,Makeup

77. Diploma in Broadcast Graphics
Sub:English,Computer,Fine Arts,Digital Arts,Web Design,Animation,Management

78. Diploma in Event Management
Sub:English,Economics,Accounts,Computer,Business Administration,Management,Fine Arts,Psychology,Leadership,Anchoring,Travelling

79. Diploma in Fashion, Textile and Apparel Design (Part Time)
Sub:English,Arithmetics,Computer,Fine arts,Handicraft & Arts,Economics,Reasearch and Observation,Digital Arts,Management

80. Diploma in Game Design And Integration
Sub:Mathematics,Computer,Computer Architecture,English,Fine Arts,Physics,Robotics & ML/AI,Cyber Security,Coding,Web Design,Animation,Logical and Reasoning,Digital Arts

81. Diploma in Graphic, Web and Multimedia Design
Sub:English,Mathematics,Fine Arts,Web Design,Computer,Cyber Security,Digital Arts,Coding,Painting

82. Diploma in Hotel and Tourism Management
Sub:English,Business Administration,Economics,Accounts,Computer,Management,Leadership,Cooking

83. Diploma in Photography and VFX (Part Time)
Sub:English,Computer,Fine Arts,Digital Arts,Photography,Travelling,Animation

84. Diploma in Photography, Videography & Cinematography
Sub:English,Computer,Fine Arts,Digital Arts,Photography,Animation,Travelling

85. Diploma in Visual Effects
Sub:Mathematics,Computer,English,Animation,Computer Architecture,Digital Arts,Coding,Fine Arts,Animation

86. B.Tech in  Electronics and Communication Engineering
sub:Physics,Mathematics ,English ,Computer ,Coding ,Electronics and Hardware,Logical and Reasoning,Computer Architecture

87. B.Tech in  Electronics and Communication
sub:Physics,Mathematics ,English ,Computer ,Coding ,Electronics and Hardware,Logical and Reasoning,Computer Architecture

88. B.Tech in  Electronics and instrumentation Engineering
sub:Physics ,Chemistry ,Mathematics ,English ,Computer ,Electronics and Hardware,Logical and Reasoning,Management,Digital Arts

89. B.Tech in Aeronautical Engineering
sub:Mathematics ,Physics ,Chemistry ,Computer,English ,Logical and Reasoning,Web Design,Computer Architecture,Outdoor Games,Electronics and Hardware,Fine Arts

90. B.Tech in Automobile Engineering
sub:Mathematics ,Physics ,Chemistry ,English, Computer ,Electronics and Hardware,Logical and Reasoning,Coding,Leadership ,Computer Architecture,Web Design,History 

91. B.Tech in Computer Engineering
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Statistics,Algebra, Cyber Security,Trigonometry,Economics,Digital Arts

92. B.Tech in Electronics and telecommunication Engineering
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Leadership ,Electronics and Hardware ,Logical and Reasoning,Coding 

93. B.Tech in Environment Engineering
sub:Chemistry,Mathematics ,Physics ,Biology ,Computer ,Geography,Environmental Science,Philosophy, Psychology,Gardening

94. B.Tech in Humanities and Social Science
sub:Mathematics, English ,Computer, Economics, Sociology, Geography History, Psychology, Leadership, Research Skills, Writing, Management, Political Science

95. B.Tech in Information and Communication Technology
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Coding ,Web Design,Electronics and Hardware,Cyber Security,Statistics,Digital Arts 

96. B.Tech in Information Technology
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Coding ,Web Design,Electronics and Hardware,Cyber Security,Statistics,Digital Arts 

97. B.Tech in Instrumentation and control Engineering
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Coding ,Web Design,Electronics and Hardware,Cyber Security,Statistics,Digital Arts ,Computer Architecture ,Logical and Reasoning,Philosophy, Psychology 

98. B.Tech in Science and Humanities
sub:Mathematics ,Physics ,Chemistry ,English, Computer,Economics ,Political Science, Sociology, History,Business Administration ,Philosophy ,Psychology,Management,Leadership,Digital Arts

99. B.Des in Animation Film Design
Sub:Mathematics,English,Computer,Fine Arts,Digital Arts,Travelling,Animation,Web Design,Computer Architecture,Coding,Trigonometry
"""
    lines = strup.split("\n")
    dict = {}
    name = ""
    for i in lines:
        if i == "\n" or i=="":
            continue
        if ". " in i:
            name = i.split(". ")[1]
        else:
            try:
                dict[name] = i.split(":")[1]
                print(name + " added")
            except Exception as e:
                print(f"Error {e} at adding " + i)
    with connection.cursor() as cursor:
        for stuff in dict.items():
            try:
                cursor.execute(f"SELECT * FROM sub_stream where name='{stuff[0]}';")
                items = list(cursor.fetchall())
                if len(items)<=0:
                    raise IndexError
                cursor.execute(f'UPDATE sub_stream SET description="{stuff[1]}" WHERE name="{stuff[0]}";')
                # print("Updated " + stuff[0])
            except Exception as e:
                try:
                    cursor.execute(f"SELECT * FROM sub_stream where name='{stuff[0]} ';")
                    items = list(cursor.fetchall())
                    if len(items)<=0:
                        raise IndexError
                    cursor.execute(f'UPDATE sub_stream SET description="{stuff[1]}" WHERE name="{stuff[0]} ";')
                    # print("Updated " + stuff[0])
                except:
                    print(f"Error {e} while updating " + stuff[0])
    return HttpResponse("Check Console")