from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django import forms


# Create your models here.

class Email(models.Model):
    Email = models.CharField(max_length=200) 
  
    def __str__(self): 
        return self.Email
    
class Contact(models.Model):
    cName=models.CharField(max_length=255)
    cEmail=models.EmailField()
    cPhone = models.PositiveBigIntegerField()
    cMsg=models.TextField()

    def __str__(self): 
        return self.cName

class User(models.Model):
    id = models.AutoField(primary_key=True)
    uName=models.CharField(max_length=255)
    uEmail=models.EmailField()
    uPass = models.CharField(max_length=255)
    uPhone = PhoneNumberField()

    def __str__(self):
        return f"{self.uName} - {self.id}"

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback=models.TextField()

    def __str__(self):
        return f"{self.submitter} - {self.feedback}"

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()

    email = models.EmailField()
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
        ('Yoga & Health','Yoga & Health'),
        ('Political Science','Political Science'),
        ('History','History'),
        ('Geography','Geography'),
        ('Accounting','Accounting'),
        ('Sociology','Sociology'),
        # Add more subjects as needed
    ]

    subject1 = models.CharField(max_length=50, choices=subject_choices)
    marks1 = models.IntegerField()

    subject2 = models.CharField(max_length=50, choices=subject_choices)
    marks2 = models.IntegerField()

    subject3 = models.CharField(max_length=50, choices=subject_choices)
    marks3 = models.IntegerField()

    skills = models.TextField(max_length=250)

    interested_subjects = models.TextField(max_length=250)

    def get_skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    def set_skills_list(self, skills_list):
        self.skills = ', '.join(skills_list)

    def get_interested_subjects_list(self):
        return [subject.strip() for subject in self.interested_subjects.split(',') if subject.strip()]

    def set_interested_subjects_list(self, interested_subjects_list):
        self.interested_subjects = ', '.join(interested_subjects_list)

    def __str__(self):
        return f" {self.id}-{self.first_name} {self.last_name} "