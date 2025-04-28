from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import BusForm
from .models import Bus, Busride
from trips.models import Trip

# Create your views here.


@login_required
def add_bus(request):
    # only drivers
    if request.user.userprofile.role != 'drv':
        return redirect('activity')
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            bus = form.save(commit=False)
            bus.driver = request.user
            bus.save()
            return redirect('activity')
    else:
        form = BusForm()
    return render(request, 'vehicles/bus_form.html', {'form': form})

@login_required
def book_ride(request):
    # only passengers
    if request.user.userprofile.role != 'psg':
        return redirect('activity')
    buses = None
    dest = request.GET.get('destination')
    if dest:
        buses = Bus.objects.filter(
            Q(stoppage1__iexact=dest) |
            Q(stoppage2__iexact=dest) |
            Q(stoppage3__iexact=dest)
        )
    return render(request, 'vehicles/bookride.html', {'buses': buses, 'dest': dest})

@login_required
def book_bus(request, bus_id):
    if request.user.userprofile.role != 'psg':
        return redirect('activity')
    bus = get_object_or_404(Bus, id=bus_id)
    if bus.vacant_seats > 0:
        bus.vacant_seats -= 1
        bus.save()
        Busride.objects.create(user=request.user, bus=bus)
        Trip.objects.create(
                user=request.user,
                bus=bus,
                destination=bus.stoppage3,
                fare=30,
                payment_status=False
            )
    return redirect('vehicles:bookride')

@login_required
def get_down(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    ride = Busride.objects.filter(user=request.user, bus=bus).first()

    if ride:
        bus.vacant_seats += 1
        bus.save()
        ride.delete()

    return redirect('activity')
