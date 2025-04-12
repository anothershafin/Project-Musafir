from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('activity/', views.activity_page, name='activity'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    #for API
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/login-otp/', views.api_login_with_otp, name='api_login_otp'),
    path('api/verify-otp/', views.api_verify_otp, name='api_verify_otp'),
    
    #for 2fa
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    #logout
    path('logout/', views.logout_view, name='logout'),
]