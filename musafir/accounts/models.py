from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.timezone import now

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



    def __str__(self):
        return self.name

#Bus route & info

class Company(models.Model):
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Driver(models.Model): # Add the new field
    about_profile= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name= models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    company= models.ForeignKey(Company, on_delete=models.CASCADE)


    def __str__(self):
        return self.name
    
class BusStop(models.Model):
    name = models.CharField(max_length=100)
    zipcode= models.CharField(max_length=10, blank=True, null=True)
    next_stop = models.CharField(max_length=100, blank=True, null=True)
    # city= models.CharField(max_length=100, blank=True, null=True)
    # country= models.CharField(max_length=100, blank=True, null=True)
    # address= models.CharField(max_length=100, blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    # edited_at = models.DateTimeField(auto_now=True)
    #latitude = models.FloatField()
    #longitude = models.FloatField()


    def __str__(self):
        return self.name


class Route(models.Model):
    id= models.AutoField(primary_key=True)
    station= models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='station', default=None)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    intermediate_stops = models.TextField(blank=True, null=True)
    map_coordinates = models.TextField(default=now)  
    created_at = models.DateTimeField(default=now)  # Timestamp for route creation
    lst=[]
    
    def path_making(self):
        point=self.start_point
        if point==self.station.name:
            while point!=self.end_point:
                self.lst.append(point)
                point=self.next_station.name
        if point==self.end_point:
            self.lst.append(point)
        self.save()
        return self.lst

    def __str__(self):
        return f"{self.start_point} to {self.end_point}"
       
# class Current_Bus(models.Model):
#     name = models.ForeignKey(Company, on_delete=models.CASCADE)
#     driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
#     capacity = models.IntegerField()
#     route = models.ForeignKey(Route, on_delete=models.CASCADE)
#     date=models.DateField(auto_now_add=True)
#     time=models.TimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} (Driver: {self.driver.name})"
    

class Ride(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    departure = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    ledger_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.departure} to {self.destination} (${self.fare})"

    
    def calculate_fare(self):
        if self.payment_status == 'unpaid':
            self.ledger_balance=(-1)*self.fare
            self.save()    

    # def complete_trip(self):
    #     if not self.is_completed:
    #         self.Ride.fare = self.fare
    #         self.user.ledger_balance -= self.fare
    #         self.user.save()
    #         self.is_completed = True
    #         self.completed_at = now()
    #         self.save()

    # def __str__(self):
    #     return f"Trip #{self.user.id} for {self.user.name}"
        

    

    def __str__(self):
        return self.name