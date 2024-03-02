from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db import connection


# Create your models here.
    
class Contact(models.Model):
    cName=models.CharField(max_length=255)
    cEmail=models.EmailField()
    cPhone = models.PositiveBigIntegerField()
    cMsg=models.TextField()

    def __str__(self): 
        return self.cName

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True)
    email=models.EmailField()

    seat_no = models.CharField(max_length=20)
    stream = models.CharField(max_length=50)

    subject_choices = [
        ('Chemistry', 'Chemistry'),
        ('Physics', 'Physics'),
        ('Biology', 'Biology'),
        ('Maths', 'Maths'),
        ('English', 'English'),
        ('Computer', 'Computer'),
        ('P.T', 'P.T'),
        ('Sanskrit', 'Sanskrit'),
        ('Accounts','Accounts'),
        ('Statistics','Statistics'),
        ('Economics','Economics'),
        ('Business Administration','Business Administration'),
        ('Gujarati','Gujarati'),
        ('Political Science','Political Science'),
        ('History','History'),
        ('Geography','Geography'),
        ('Accounting','Accounting'),
        ('Sociology','Sociology'),
        # Add more subjects as needed
    ]

    subject1 = models.CharField(max_length=50, choices=subject_choices)
    marks1 = models.IntegerField(default=0)

    subject2 = models.CharField(max_length=50, choices=subject_choices)
    marks2 = models.IntegerField(default=0)

    subject3 = models.CharField(max_length=50, choices=subject_choices)
    marks3 = models.IntegerField(default=0)

    skills = models.TextField(max_length=250)

    interested_subjects = models.TextField(max_length=250)

    result = models.TextField(max_length=250)
    score = models.IntegerField(default=-1)

    def get_skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    def set_skills_list(self, skills_list):
        self.skills = ', '.join(skills_list)

    def get_interested_subjects_list(self):
        return [subject.strip() for subject in self.interested_subjects.split(',') if subject.strip()]

    def set_interested_subjects_list(self, interested_subjects_list):
        self.interested_subjects = ', '.join(interested_subjects_list)

    def __str__(self):
        return f"{self.id}"

class User(models.Model):
    id = models.AutoField(primary_key=True)
    uName=models.CharField(max_length=255,unique=True)
    uEmail=models.EmailField()
    uPass = models.CharField(max_length=255)
    uPhone = PhoneNumberField()
    Student = models.ForeignKey(Student, on_delete=models.SET_DEFAULT,default=1)

    def __str__(self):
        return f"{self.uName} - {self.id}"

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback=models.TextField()

    def __str__(self):
        return f"{self.submitter} - {self.feedback}"

class MCQ(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=255,default="timepass")
    question = models.TextField(max_length=255)
    optionA = models.TextField(max_length=255)
    optionB = models.TextField(max_length=255)
    optionC = models.TextField(max_length=255)
    optionD = models.TextField(max_length=255)
    correct = models.CharField(max_length=2)
    def __str__(self):
        return f"{self.subject} {self.id}"

class Stream(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(default="null",blank=True)
    fees = models.CharField(max_length=255,blank=True,default=-1)
    description = models.TextField(max_length=255,default="Null",blank=True)
    college_name = models.ForeignKey('College', on_delete=models.CASCADE,blank=True)
    def __str__(self):
        return f"{self.name} {self.college_name}"

class College(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(default="null")
    address = models.TextField(max_length=255,blank=True)
    placement = models.CharField(max_length=255,blank=True)
    hostel = models.CharField(max_length=255,blank=True)
    transport = models.CharField(max_length=255,blank=True)
    link = models.TextField(max_length=255,blank=True)
    courses = models.ManyToManyField("Stream",blank=True)
    def get_streams(self):
        # Return all Stream instances related to this College
        # with connection.cursor() as cursor:
        #     cursor.execute(f"SELECT * FROM sub_stream WHERE college_name_id='{id}'")
        #     temp = list(cursor.fetchall())
        # return temp
        return self.courses.all()
    def __str__(self):
        return f"{self.name}"
