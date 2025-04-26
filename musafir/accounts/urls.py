from django.contrib import admin
from django.urls import path
from . import views
#Farhan Hossain Sajid
from django.views.generic import TemplateView
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    #Farhan Hossain Sajid 
    #path('activity/', views.activity_page, name='activity'),
    path('activity/', views.activity_view, name='activity'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    #for API
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/login-otp/', views.api_login_with_otp, name='api_login_otp'),
    path('api/verify-otp/', views.api_verify_otp, name='api_verify_otp'),
    path('api/profile/', views.api_profile_view, name='api_profile_view'),
    
    #for 2fa
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    #logout
    path('logout/', views.logout_view, name='logout'),
    #path('send-emergency-text/', views.send_emergency_text, name='send_emergency_text'),
    path('send-emergency-email/', views.send_emergency_email, name='send_emergency_email'),
    path('activity/', views.activity_view, name='activity'),
    path('new-page/', views.new_page_view, name='new_page'),
    path("upload/", views.upload_image, name="upload_image"),





    # demo-only: serve the static mockup
    path('ratings/confirmation/',
        TemplateView.as_view(template_name='accounts/rating_confirmation.html'),
        name='rating_confirmation'),


]