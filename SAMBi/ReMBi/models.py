from django.db import models
import random
import string


# Create your models here.



class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    token = models.TextField()
    key = models.TextField()

    def __str__(self):
        return self.username
    

class Face(models.Model):
    id_face = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    face_data = models.ImageField(upload_to='face/', default=None)

class Voice(models.Model):
    id_voice = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    voice_data = models.FileField(upload_to='voice/', default=None)

class Finger(models.Model):
    id_finger = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    finger_data = models.ImageField(upload_to='finger/', default=None)

class Person(models.Model):
    id_person = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=320)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name + self.last_name

class Logs(models.Model):
    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date_time = models.DateTimeField(auto_now_add=True, editable=False)

