from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Register(AbstractUser):
    name = models.CharField(max_length=255)
    rollnum = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    year = models.IntegerField(default=0)
    password = models.CharField(max_length=500)
    isAdmin = models.BooleanField(default=False)
    isVerified = models.BooleanField(default=False)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "mobile", "password", "department"]
