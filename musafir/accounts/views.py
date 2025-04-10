from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Create your views here.
def home(request):
    return render(request, 'accounts/home.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # Not saved here unless you use a custom model
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'accounts/signup.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': "Username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password)
        # You can save role and phone in a profile model if you want to store them
        login(request, user)  # auto-login after registration

        return redirect('home')  # change to your homepage route

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