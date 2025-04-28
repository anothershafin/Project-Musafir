from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from .models import Trip

def make_payment(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    trip.payment_status = True
    trip.save()
    return redirect('activity')

from django.db.models import Sum

def past_rides(request):
    trips = Trip.objects.filter(user=request.user)
    total_bill = trips.aggregate(Sum('fare'))['fare__sum'] or 0
    paid_amount = trips.filter(payment_status=True).aggregate(Sum('fare'))['fare__sum'] or 0
    unpaid_amount = total_bill - paid_amount
    return render(request, 'trips/pastrides.html', {
        'trips': trips,
        'total_bill': total_bill,
        'paid_amount': paid_amount,
        'unpaid_amount': unpaid_amount,
    })