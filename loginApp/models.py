from django.db import models
from masterApp.models import *

class Registeruse(models.Model):
    role = models.ForeignKey(Role,on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15,unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)