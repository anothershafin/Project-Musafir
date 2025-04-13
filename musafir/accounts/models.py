from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=[('psg', 'Passenger'), ('drv', 'Driver')])
    is_two_step_verified = models.BooleanField(default=False)  # 👈 Add this here
    emergency_contact = models.CharField(
        max_length=154,
        blank=True,
        null=True,)
    emergency_message = models.TextField(blank=True, null=True)  # New field
    
    
    def __str__(self):
        return self.user.username
    
class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.created_at = datetime.now()
        self.save()
        
        
class Ride(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    departure = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.departure} to {self.destination} (${self.fare})"
        