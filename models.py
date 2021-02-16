from django.conf import settings
from django.db import models

from django.core.files import File
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.


class Fuel_name (models.Model):
    fuel_name = models.CharField(max_length=200, null = True) 

    def __str__(self):
        return self.fuel_name

class Fuel_price (models.Model):
    fuel_name = models.ForeignKey(Fuel_name, on_delete=models.CASCADE, null=True) 
    fuel_price = models.DecimalField(max_digits=8, decimal_places=2, null=True) 
    date_entered = models.DateTimeField(auto_now=True, null=True)

