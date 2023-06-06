
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import SignUpForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

def index(request):
    return render(request,'index.html')



def signup(request):
    User = get_user_model()

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            # Check if email already exists
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please use a different email.')
            else:
                form.save()

                # Authenticate user
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    # Login user
                    login(request, user)
                    # Redirect to sign-in page
                    return redirect(reverse('signin'))
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()

    # Display the registration form
    return render(request, 'signup.html', {'form': form})






from .forms import SignInForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignInForm

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Login user
                login(request, user)
                # Redirect to home page or a success page
                return redirect('home')
    else:
        form = SignInForm()

    # Display the login form
    return render(request, 'signin.html', {'form': form})



@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    logout(request)
    return render(request, 'logout.html')
