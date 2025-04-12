from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=[('psg', 'Passenger'), ('drv', 'Driver')])
    is_two_step_verified = models.BooleanField(default=False)  # 👈 Add this here

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
        
        