from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required
#for api
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginRequestSerializer, OTPVerifySerializer
#2fa
from django.core.mail import send_mail
from .models import EmailOTP, UserProfile
from django.contrib.auth import authenticate
import random
#logout
from django.contrib.auth import logout


# Create your views here.
def home(request):
    return render(request, 'accounts/home.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'accounts/signup.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': "Username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, phone=phone, role=role)
        login(request, user) 

        return redirect('activity')

    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'accounts/login.html', {'error': 'User with this email does not exist'})

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('activity')  # Placeholder page
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    profile = request.user.userprofile
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile
    })

@login_required
def profile_update(request):
    profile = request.user.userprofile  # Access related profile

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role')

        request.user.username = username
        request.user.email = email
        request.user.save()

        profile.phone = phone
        profile.role = role
        profile.save()

        return redirect('profile')

    return render(request, 'accounts/profile_update.html', {
        'user': request.user,
        'profile': profile
    })
    
@login_required
def activity_page(request):
    return render(request, 'accounts/activity.html')

#2fa
def send_otp(request):
    user = request.user
    otp, _ = EmailOTP.objects.get_or_create(user=user)
    otp.generate_otp()

    send_mail(
        'Your OTP for 2-Step Verification',
        f'Your OTP is: {otp.otp}',
        'shafin.armstrong5@gmail.com',  
        [user.email],
        fail_silently=False,
    )

    return redirect('verify_otp')

@login_required
def verify_otp(request):
    user = request.user
    try:
        otp_entry = EmailOTP.objects.get(user=user)
    except EmailOTP.DoesNotExist:
        return redirect('profile')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == otp_entry.otp and not otp_entry.is_expired():
            profile = UserProfile.objects.get(user=user)
            profile.is_two_step_verified = True
            profile.save()
            otp_entry.delete()  #otp clear er jonno
            return redirect('profile')
        else:
            return render(request, 'accounts/verify_otp.html', {'error': 'Invalid or expired OTP'})

    return render(request, 'accounts/verify_otp.html')

def logout_view(request):
    logout(request)
    return redirect('home')

#for API
@api_view(['POST'])
def api_signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_login(request):
    from django.contrib.auth import authenticate
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    user = authenticate(username=user.username, password=password)
    if user is not None:
        return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def api_login_with_otp(request):
    serializer = LoginRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        user = authenticate(username=user.username, password=password)
        if user:
            otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()
            send_mail(
                subject='Your Musafir OTP Code',
                message=f'Your OTP is {otp_obj.otp}. It will expire in 5 minutes.',
                from_email='yourgmail@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({'message': 'OTP sent to your email'}, status=200)
        else:
            return Response({'error': 'Invalid password'}, status=400)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def api_verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)
            if otp_obj.otp == otp:
                if otp_obj.is_expired():
                    return Response({'error': 'OTP expired'}, status=400)
                return Response({'message': 'OTP verified. Login successful!'}, status=200)
            else:
                return Response({'error': 'Invalid OTP'}, status=400)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({'error': 'Invalid request'}, status=400)
    return Response(serializer.errors, status=400)