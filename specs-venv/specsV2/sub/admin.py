from django import forms
from django.utils.html import format_html
from django.contrib import admin
from .models import *
from django.contrib.admin.views import main

# Register your models here.

admin.site.register(User)
admin.site.register(Feedback)
admin.site.register(Contact)
admin.site.register(Student)
admin.site.register(MCQ)
class CollegeAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses',)
admin.site.register(College,CollegeAdmin)
admin.site.register(Stream)