from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django import forms
from django.contrib.postgres.fields import ArrayField


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
    first_name = models.CharField(max_length=255,blank=True)
    last_name = models.CharField(max_length=255,blank=True)
    date_of_birth = models.DateField(null=True)

    email = models.EmailField(blank=True)
    seat_no = models.CharField(max_length=20,blank=True)
    stream = models.CharField(max_length=50,blank=True)

    subject_choices = [
        ('Chemistry', 'Chemistry'),
        ('Physics', 'Physics'),
        ('Biology', 'Biology'),
        ('Maths', 'Maths'),
        ('English', 'English'),
        ('Computer', 'Computer'),
        ('P.T', 'P.T'),
        ('Sanskrit', 'Sanskrit'),
        # Add more subjects as needed
    ]

    subject1 = models.CharField(max_length=50, choices=subject_choices,blank=True)
    marks1 = models.IntegerField(null=True)

    subject2 = models.CharField(max_length=50, choices=subject_choices,blank=True)
    marks2 = models.IntegerField(null=True)

    subject3 = models.CharField(max_length=50, choices=subject_choices,blank=True)
    marks3 = models.IntegerField(null=True)

    skills = models.ArrayField(models.CharField(max_length=50), blank=True, null=True)

    interested_subjects = models.ArrayField(models.CharField(max_length=50), blank=True, null=True)

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