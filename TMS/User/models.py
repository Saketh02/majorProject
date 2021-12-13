from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Register(AbstractUser):
    name = models.CharField(max_length=255)
    rollnum = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    year = models.IntegerField(default=0)
    password = models.CharField(max_length=30)

    REQUIRED_FIELDS = ["name", "email", "mobile", "password", "department"]
