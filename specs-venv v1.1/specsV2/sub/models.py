from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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