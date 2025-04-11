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
from .models import EmailOTP
from django.contrib.auth import authenticate


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

def activity_page(request):
    return HttpResponse("<h1>Welcome to Project Musafir Activity Page!</h1>")

@login_required
def profile_view(request):
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

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile
    })
    
@login_required
def activity_page(request):
    return render(request, 'accounts/activity.html')

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