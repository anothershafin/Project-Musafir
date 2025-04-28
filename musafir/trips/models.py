from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from vehicles.models import Bus  # Import your Bus model

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    destination = models.CharField(max_length=255)
    fare = models.IntegerField(default=30)  # 30 taka for apatoto test
    payment_status = models.BooleanField(default=False)  # False = Unpaid, True = Paid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bus.bus_name}"