from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Bus(models.Model):
    driver          = models.ForeignKey(User, on_delete=models.CASCADE)
    bus_name        = models.CharField(max_length=100)
    route           = models.CharField(max_length=200)
    stoppage1       = models.CharField(max_length=100)
    stoppage2       = models.CharField(max_length=100)
    stoppage3       = models.CharField(max_length=100)
    total_seats     = models.PositiveIntegerField()
    vacant_seats    = models.PositiveIntegerField()
    current_location= models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.bus_name} ({self.route})"