from django.db import models

# Create your models here.

class Role(models.Model):
    role_name = models.CharField(max_length=25, unique=True)

class User(models.Model):
    user_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.IntegerField()
    std = models.IntegerField()

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=25)