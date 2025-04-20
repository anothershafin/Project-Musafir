from django import forms
from .models import Bus

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_name','route',
            'stoppage1','stoppage2','stoppage3',
            'total_seats','vacant_seats',
            'current_location',
        ]