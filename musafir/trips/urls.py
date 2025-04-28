from django.urls import path
from . import views

urlpatterns = [
    path('make-payment/<int:trip_id>/', views.make_payment, name='make_payment'),
    path('past-rides/', views.past_rides, name='past_rides'),
]