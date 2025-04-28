from django.urls import path
from . import views

app_name = 'vehicles'
urlpatterns = [
    path('add-bus/',   views.add_bus,   name='add_bus'),
    path('book-ride/', views.book_ride, name='bookride'),
    path('book/<int:bus_id>/', views.book_bus, name='book_bus'),
    path('get_down/<int:bus_id>/', views.get_down, name='get_down'),
]