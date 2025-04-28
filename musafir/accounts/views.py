from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required
#for api
from rest_framework.decorators import api_view , permission_classes 
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginRequestSerializer, OTPVerifySerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
#2fa
from django.core.mail import send_mail
from .models import EmailOTP, UserProfile
from django.contrib.auth import authenticate
import random
#logout
from django.contrib.auth import logout


#from twilio.rest import Client

from django.core.mail import send_mail

from .models import Ride
from trips.models import Trip



import cv2
import pytesseract
import re
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage



# Create your views here.
def home(request):
    # Example static coordinates for now
    bus_data = [
        {"name": "Bus 1", "lat": 23.8103, "lon": 90.4125},
        {"name": "Bus 2", "lat": 23.8150, "lon": 90.4200},
    ]
    return render(request, 'accounts/home.html', {"bus_data": bus_data})

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
        profile.emergency_contact = request.POST.get('emergency_contact')
        profile.emergency_message = request.POST.get('emergency_message')
        profile.save()

        return redirect('profile')

    return render(request, 'accounts/profile_update.html', {
        'user': request.user,
        'profile': profile
    })
    
@login_required
def activity_page(request):
    trips = Trip.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/activity.html', {
        'trips': trips,
    })

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
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=404)

    user = authenticate(request, username=user.username, password=password)
    if user is not None:
        login(request, user)  # ✅ This is what creates sessionid
        return Response({'message': 'Login successful', 'username': user.username}, status=200)
    else:
        return Response({'error': 'Invalid credentials'}, status=400)
    
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
                from_email='shafin.armstrong5@gmail.com',
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile_view(request):
    profile = request.user.userprofile
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

##############################################################################

@login_required
def send_emergency_email(request):
    # Recipient's email address (e.g., from the user's profile)
    recipient_email = request.user.email  # Or use a custom field if needed
    emergency_contact_email = request.user.userprofile.emergency_contact  # Optional: Add an email field for emergency contact

    # Email subject and message
    subject = "Emergency Alert"
    message =  request.user.userprofile.emergency_message 
    from_email = 'your_email@gmail.com'  # Replace with your email

    # Send email
    try:
        send_mail(
            subject,
            message,
            from_email,
            [recipient_email], 
            fail_silently=False,
        )
        return HttpResponse("Emergency email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send emergency email: {str(e)}", status=500)

@login_required
def activity_view(request):
    # Fetch past rides for the logged-in user
    past_rides = Ride.objects.filter(user=request.user).order_by('-date')  # Adjust based on your model
    return render(request, 'accounts/activity.html', {'past_rides': past_rides})





def new_page_view(request):
    return render(request, 'accounts/new_page.html')


def upload_image(request):
    student_id = None
    error_message = None

    if request.method == "POST" and request.FILES.get("image"):
        if request.user.is_authenticated and request.user.userprofile.is_student:
            error_message = "Already verified"
        else:
            # Save the uploaded file
            image_file = request.FILES["image"]
            fs = FileSystemStorage()
            file_path = fs.save(image_file.name, image_file)
            file_url = fs.path(file_path)

            try:
                # Load the image using OpenCV
                image = cv2.imread(file_url)

                if image is None:
                    error_message = "Error: Could not load the uploaded image."
                else:
                    # Convert the image to grayscale
                    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    # Apply thresholding to improve text contrast
                    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

                    # Perform OCR on the preprocessed image
                    extracted_text = pytesseract.image_to_string(thresh_image)

                    # Use regex to find an 8-digit student ID
                    match = re.search(r'\b\d{8}\b', extracted_text)
                    if match:
                        student_id = match.group()
                        # Set the is_student flag to True for the logged-in user
                        if request.user.is_authenticated:
                            user_profile = request.user.userprofile
                            user_profile.is_student = True
                            user_profile.save()
                    else:
                        error_message = "No 8-digit student ID found in the image. Please try again."

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"

            # Delete the uploaded file after processing
            fs.delete(file_path)

        return render(request, "accounts/new_page.html", {"student_id": student_id, "error_message": error_message})





# Map view for bus tracking

def map_view(request):
    # Example static coordinates for now
    bus_data = [
        {"name": "Bus 1", "lat": 23.8103, "lon": 90.4125},
        {"name": "Bus 2", "lat": 23.8150, "lon": 90.4200},
    ]
    return render(request, 'accounts/map.html', {"bus_data": bus_data})
