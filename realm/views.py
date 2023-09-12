from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SignInForm, SignUpForm
from .models import Profile
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import SignInForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import SignInForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib import messages


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

import random
import requests
from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from .forms import SignInForm


def index(request):
    return render(request, "index.html")


User = get_user_model()

from realm.models import CustomUser


API_KEY = "2f5f524a-488e-11ee-addf-0200cd936042"

from django.shortcuts import redirect


def signin(request):
    if request.method == "POST":
        if "mobile" in request.POST:
            try:
                user_mobile_number = request.POST["mobile"]
                user = CustomUser.objects.get(mobile_number=user_mobile_number)
                print(user)
                # Generate a random OTP
                otp = str(random.randint(100000, 999999))

                # Send OTP to the user's mobile number
                send_otp_url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{user_mobile_number}/{otp}"

                response = requests.post(send_otp_url)
                if response.status_code == 200:
                    # OTP sent successfully
                    request.session["session_id"] = response.json().get("Details")
                    request.session[
                        "mobile_number"
                    ] = user_mobile_number  # Store mobile number in session
                    return render(
                        request,
                        "otp_verification.html",
                        {"mobile_number": user_mobile_number},
                    )

                # Failed to send OTP
                error_message = response.json().get("Status")
                return render(request, "signin.html", {"error_message": error_message})

            except CustomUser.DoesNotExist:
                error_message = "Invalid or non-existent mobile number."
                return render(request, "signin.html", {"error_message": error_message})

        # Process the username and password login
        username = request.POST["username"]
        password = request.POST["password"]

        if username == "admin" and password == "admin123":
            form = VideoUploadForm(request.POST, request.FILES)
            # Special case for username 'anitha' and password 'anitha123'
            return redirect(movie_upload)

        if "otp" in request.POST:
            otp = request.POST["otp"]
            session_id = request.session.get("session_id")
            mobile_number = request.session.get("mobile_number")
            # Verify the OTP
            verify_otp_url = (
                f"https://2factor.in/API/V1/{API_KEY}/SMS/VERIFY/{session_id}/{otp}"
            )

            response = requests.get(verify_otp_url)
            if (
                response.status_code == 200
                and response.json().get("Status") == "Success"
            ):
                # OTP verification successful
                user = authenticate(
                    request, username=mobile_number, password=""
                )  # Authenticate with mobile number

                if user is not None:
                    # User is authenticated
                    login(request, user)

                    # Fetch the profiles of the signed-in user
                    profiles = Profile.objects.filter(user=user)

                    if profiles.exists():
                        return render(request, "profile.html", {"profiles": profiles})
                    else:
                        # No profiles found for the user, redirect to profiles page
                        return redirect("profiles")

                else:
                    # Authentication failed
                    error_message = "Invalid username or password."
                    return render(
                        request, "signin.html", {"error_message": error_message}
                    )
            else:
                # OTP verification failed
                error_message = "Invalid OTP."
                return render(request, "signin.html", {"error_message": error_message})

        else:
            # Normal authentication flow
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # User is authenticated
                login(request, user)

                # Fetch the profiles of the signed-in user
                profiles = Profile.objects.filter(user=user)

                if profiles.exists():
                    return render(request, "profile.html", {"profiles": profiles})
                else:
                    # No profiles found for the user, redirect to profiles page
                    return redirect("profiles")

            else:
                # Authentication failed
                error_message = "Invalid username or password."
                return render(request, "signin.html", {"error_message": error_message})

    return render(request, "signin.html")


import requests


def otp_verification(request):
    user_mobile_number = request.session.get("mobile_number")
    if request.method == "POST":
        user_entered_otp = ""
        for i in range(1, 7):
            digit = request.POST.get(f"otp{i}")
            if not digit or not digit.isdigit():
                error_message = "Please enter a valid OTP."
                return render(
                    request,
                    "otp_verification.html",
                    {
                        "error_message": error_message,
                        "mobile_number": user_mobile_number,
                    },
                )
            user_entered_otp += digit

        session_id = request.session.get("session_id")
        # Verify the entered OTP
        verify_otp_url = f"https://2factor.in/API/V1/{API_KEY}/SMS/VERIFY/{session_id}/{user_entered_otp}"

        response = requests.post(verify_otp_url)
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get("Status") == "Success":
                # OTP verification successful

                # Get the user associated with the mobile number
                try:
                    user = CustomUser.objects.get(mobile_number=user_mobile_number)
                except CustomUser.DoesNotExist:
                    error_message = "Invalid or non-existent mobile number."
                    return render(
                        request,
                        "otp_verification.html",
                        {
                            "error_message": error_message,
                            "mobile_number": user_mobile_number,
                        },
                    )

                # Fetch the profiles associated with the user
                profiles = Profile.objects.filter(user=user)

                if profiles.exists():
                    return render(request, "profile.html", {"profiles": profiles})
                else:
                    # No profiles found for the user, redirect to profiles page
                    return redirect("profiles")

            else:
                # OTP verification failed
                error_message = json_response.get("Details")
                return render(
                    request,
                    "otp_verification.html",
                    {
                        "error_message": error_message,
                        "mobile_number": user_mobile_number,
                    },
                )

        # Failed to verify OTP
        error_message = "Failed to verify OTP."
        return render(
            request,
            "otp_verification.html",
            {"error_message": error_message, "mobile_number": user_mobile_number},
        )

    return render(
        request, "otp_verification.html", {"mobile_number": user_mobile_number}
    )


from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import Profile


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            username = form.cleaned_data["username"]
            mobile_number = form.cleaned_data["mobile_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Check if the username, email, or mobile number already exist
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
            elif User.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, "Mobile number is already in use.")
            else:
                # Create a new user
                user = User.objects.create_user(
                    username=username, password=password, email=email
                )
                user.mobile_number = (
                    mobile_number  # Save the mobile number in the user model
                )
                user.save()

                # Create a default profile for the user during signup
                profile_name = username
                profile = Profile(
                    user=user, name=profile_name, mobile_number=mobile_number
                )
                profile.save()

                login(request, user)
                subject = "Signup Success"
                context = {"username": username}
                html_message = render_to_string("signup_success_email.html", context)
                plain_message = strip_tags(html_message)
                from_email = "realmdefend@gmail.com"
                to_email = user.email

                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [to_email],
                    html_message=html_message,
                )
                return redirect("signin")
        else:
            # If the form is not valid, display the error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


from .forms import VideoUploadForm
from .models import Video


import zipfile
import os


def movie_upload(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)

            # Save the video and thumbnail files
            video.video_file = request.FILES["video_file"]
            video.thumbnail = request.FILES["thumbnail"]
            video.save()

            # Unzip the video file if it is a zip file
            if video.video_file.name.endswith(".zip"):
                zip_file_path = video.video_file.path
                target_directory = os.path.dirname(zip_file_path)

                with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                    zip_ref.extractall(target_directory)

                # Remove the zip file after extraction
                os.remove(zip_file_path)

                # Change the value of video_file to have .m3u8 extension
                new_video_file_name = (
                    os.path.splitext(video.video_file.name)[0] + ".m3u8"
                )
                video.video_file.name = new_video_file_name
                video.save(update_fields=["video_file"])

            return redirect(
                "movie_upload"
            )  # Redirect to the videos page after successful upload
    else:
        form = VideoUploadForm()
    return render(request, "video_upload.html", {"form": form})


from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    # Retrieve the logged-in user
    user = request.user
    # Retrieve all profiles associated with the logged-in user
    profiles = Profile.objects.filter(user=user)
    return render(request, "profile.html", {"user": user, "profiles": profiles})


@login_required

def add_profile(request):
    user = request.user
    profile_count = Profile.objects.filter(user=user).count()

    if profile_count >= 4:
        return redirect("profile")

    if request.method == "POST":
        profile_name = request.POST["profile_name"]
        profile_photo = request.FILES.get(
            "profile_photo"
        )  # Updated field name to 'profile_photo'
        child_profile = request.POST.get("child_profile")
        pin = request.POST.get("pin")  # Get the 'pin' value from the form
        confirm_pin = request.POST.get("cpin")

        if pin == confirm_pin:
            child_profile = True if child_profile == "1" else False

            existing_profile = Profile.objects.filter(
                user=user, name=profile_name
            ).first()
            if existing_profile:
                error_message = "Profile name already exists"
                return render(
                    request,
                    "add_profile.html",
                    {"add_profile_disabled": False, "error_message": error_message},
                )

            profile = Profile(
                user=user,
                name=profile_name,
                photo=profile_photo,
                child_profile=child_profile,
                pin=pin,
            )  # Save 'pin' to the profile
            profile.save()

            profile_count += 1
            if profile_count >= 4:
                add_profile_disabled = True
            else:
                add_profile_disabled = False

            return redirect("profiles")
        else:
            error_message = "PIN and Confirm PIN do not match"
            return render(
                request,
                "add_profile.html",
                {"add_profile_disabled": False, "error_message": error_message},
            )

    return render(request, "add_profile.html", {"add_profile_disabled": False})

def edit_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    is_first_profile = Profile.objects.filter(user=request.user).first() == profile
    
    if request.method == "POST":
        name = request.POST.get("name")
        profile.name = name
        
        if "profile_picture" in request.FILES:
            profile.photo = request.FILES["profile_picture"]
        
        new_pin = request.POST.get("new_pin")  # New PIN entered during editing
        confirm_pin = request.POST.get("confirm_pin")  # Confirmed PIN
        
        if new_pin:
            if new_pin == confirm_pin:
                profile.pin = new_pin  # Set the new PIN if provided and confirmed
            else:
                # Handle error: Entered PIN and Confirm PIN do not match
                error_message = "Entered PIN and Confirm PIN do not match."
                context = {
                    "profile": profile,
                    "is_first_profile": is_first_profile,
                    "error_message": error_message,
                }
                return render(request, "edit_profile.html", context)
        elif not profile.pin:
            profile.pin = None  # Retain old PIN if not provided during editing
        
        profile.save()
        
        return redirect("profiles")
    
    context = {
        "profile": profile,
        "is_first_profile": is_first_profile,
    }
    return render(request, "edit_profile.html", context)




def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if profile.user == request.user:  # User owns the profile
        return render(request, "profile_detail.html", {"profile": profile})

    if profile == Profile.objects.filter(user=request.user).first():  # Default profile
        if request.method == "POST":
            entered_pin = request.POST.get("pin")
            if entered_pin == profile.pin:
                return render(request, "profile_detail.html", {"profile": profile, "can_edit": True})

        return render(request, "pin_verification.html", {"profile": profile})

    return render(request, "profile_detail.html", {"profile": profile})


def delete_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    profile.delete()
    return redirect("profiles")


from django.shortcuts import get_object_or_404
from .models import Genres, Video


from django.shortcuts import render


def player(request, video_id):
    video = Video.objects.get(id=video_id)
    video_url = video.video_file.url
    print(video_url)
    return render(request, "player.html", {"video_url": video_url})


import datetime


def home(request):
    categories = Genres.objects.all()
    videos = Video.objects.all()

    genre_id = request.GET.get("genre_id")
    if genre_id:
        genre = get_object_or_404(Genres, id=genre_id)
        videos = videos.filter(genres=genre)

    return render(
        request, "category_list.html", {"categories": categories, "videos": videos}
    )


def schedule(request):
    current_time = datetime.datetime.now()
    videos = Video.objects.filter(scheduled_time__lte=current_time)
    return render(request, "scheduled_video.html", {"videos": videos})


def video_list(request, genre_id):
    genre = Genres.objects.get(pk=genre_id)
    videos = Video.objects.filter(genres=genre)
    thumbnails = Video.objects.all()
    context = {"genre": genre, "videos": videos, "thumbnails": thumbnails}
    return render(request, "video_list.html", context)


def search(request):
    videos = Video.objects.all()
    return render(request, "search.html", {"videos": videos})

def movies(request):
    videos = Video.objects.all()
    return render(request, "movies.html", {"videos": videos})




def search_kids(request):
    videos = Video.objects.exclude(content_age_rating="18+")
    return render(request, "search1.html", {"videos": videos})


def kid_home(request):
    categories = Genres.objects.all()
    videos = Video.objects.exclude(content_age_rating="18+")
    genre_id = request.GET.get("genre_id")
    if genre_id:
        genre = get_object_or_404(Genres, id=genre_id)
        videos = videos.filter(genres=genre)

    return render(request, "home1.html", {"categories": categories, "videos": videos})


def home_kids(request):
    categories = Genres.objects.exclude(
        name__in=["Crime", "Thriller", "Romantic", "Horror"]
    )
    videos = Video.objects.exclude(content_age_rating="18+")

    genre_id = request.GET.get("genre_id")
    if genre_id:
        genre = get_object_or_404(Genres, id=genre_id)
        videos = videos.filter(genres=genre)

    return render(
        request, "category_list1.html", {"categories": categories, "videos": videos}
    )


def video_list1(request, genre_id):
    genre = Genres.objects.get(pk=genre_id)
    videos = Video.objects.filter(genres=genre).exclude(content_age_rating="18+")
    thumbnails = Video.objects.all()
    context = {"genre": genre, "videos": videos, "thumbnails": thumbnails}
    return render(request, "video_list1.html", context)


def logout_view(request):
    logout(request)
    return redirect("index")


def movie_details(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, "movie.html", {"video": video})


# views.py
def unlock_pin(request):
    if request.method == "POST":
        name = request.POST.get("profilename", "")
        digit1 = request.POST.get("digit1", "")
        digit2 = request.POST.get("digit2", "")
        digit3 = request.POST.get("digit3", "")
        digit4 = request.POST.get("digit4", "")

        submitted_pin = digit1 + digit2 + digit3 + digit4

        # Assuming you have a Profile model with 'pin', 'child_profile', 'name', and 'user' fields
        from .models import Profile

        try:
            # Get the currently logged-in user
            user = request.user

            # Filter profiles for the current user based on the provided name
            profile = Profile.objects.get(user=user, name=name)

            # Check the submitted PIN against the fetched profile's PIN
            if profile.pin == submitted_pin:
                child_profile = profile.child_profile
                print("Child Profile:", child_profile)  # Print the value for debugging

                if child_profile == 0:
                    return redirect("home")
                else:
                    return redirect("home_kids")
            else:
                return render(request, "pin.html", {"error_message": "Invalid PIN"})

        except Profile.DoesNotExist:
            # Profile does not exist
            return render(request, "pin.html", {"error_message": "Invalid Name"})
    else:
        # GET request or other method
        return render(request, "pin.html")


from django.urls import reverse


# views.py
from django.shortcuts import get_object_or_404

def unlock(request):
    if request.method == "POST":
        name = request.POST.get("profilename", "")
        digit1 = request.POST.get("digit1", "")
        digit2 = request.POST.get("digit2", "")
        digit3 = request.POST.get("digit3", "")
        digit4 = request.POST.get("digit4", "")

        submitted_pin = digit1 + digit2 + digit3 + digit4

        # Assuming you have a Profile model with 'pin', 'child_profile', 'name', and 'user' fields
        from .models import Profile

        try:
            # Get the currently logged-in user
            user = request.user

            # Filter profiles for the current user based on the provided name
            profile = get_object_or_404(Profile, user=user, name=name)

            # Check the submitted PIN against the fetched profile's PIN
            if profile.pin == submitted_pin:
                edit_profile_url = reverse("edit_profile", args=[profile.id])
                return redirect(edit_profile_url)
            else:
                return render(
                    request, "pin_edit.html", {"error_message": "Invalid PIN"}
                )

        except Profile.DoesNotExist:
            # Profile does not exist
            return render(request, "pin_edit.html", {"error_message": "Invalid Name"})
    else:
        # GET request or other method
        return render(request, "pin_edit.html")





from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def toggle_watchlist(request, video_id):
    video = Video.objects.get(pk=video_id)
    user_profile = request.user.userprofile
    
    if video in user_profile.watchlist.all():
        user_profile.watchlist.remove(video)
        added = False
    else:
        user_profile.watchlist.add(video)
        added = True
    
    return JsonResponse({'added': added})



from django.http import JsonResponse
from .models import Notification
def get_notifications(request):
    latest_notifications = Notification.objects.select_related("video").order_by(
        "-timestamp"
    )[:5]
    notifications_data = [
        {
            "video": notification.video.title,
            "timestamp": notification.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for notification in latest_notifications
    ]
    return JsonResponse(notifications_data, safe=False)


#----------------------------forgotpasswordpage----------------------------------------------------------------------
# views.py
# import random
# import smtplib
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import get_user_model, login
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from .models import Profile  # Import your Profile model here
# from .forms import SignUpForm  # Import your SignUpForm here

# def forgotpassword(request):
#     otp = ''
#     if request.method == 'POST':
#         user = request.POST.get('username')
#         email = request.POST.get('email')
#         print(user, email)
#         if get_user_model().objects.filter(username=user, email=email).exists():
#             user_obj = get_user_model().objects.get(username=user, email=email)
#             mail = user_obj.email
#             id = str(user_obj.id)
#             print(id, type(id))
#             print('exists', mail)
#             from_addr = "adandge805@gmail.com"
#             password = "hdyvxcfrrbqfzgqp"
            
#             no = str(random.randint(111111, 999999))  # Fix the OTP generation
            
#             msg = f"""
# Verification Code for RESET PASSWORD: {no}
#             """
#             otp = f"{no},{id}"
#             server = smtplib.SMTP('smtp.gmail.com:587')
#             server.starttls()
#             server.login(from_addr, password)
#             print("Login Successful")
#             server.sendmail(from_addr, mail, msg)
#             print(msg)
#             print("OTP Successfully Sent...")
#             server.quit()
#             messages.success(request, "OTP Successfully Sent...")
#             return render(request, 'validate.html', {'otp': otp, 'disotp': 'block', 'disreset': 'none'})
#         else:
#             print('not exists')
#             messages.error(request, "Enter Valid Details !")
#             return render(request, 'forgotpassword.html')

#     return render(request, 'forgotpassword.html')

# def signup(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             User = get_user_model()
#             username = form.cleaned_data["username"]
#             mobile_number = form.cleaned_data["mobile_number"]
#             email = form.cleaned_data["email"]
#             password = form.cleaned_data["password"]

#             # Check if the username, email, or mobile number already exist
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, "Username is already taken.")
#             elif User.objects.filter(email=email).exists():
#                 messages.error(request, "Email is already registered.")
#             elif User.objects.filter(mobile_number=mobile_number).exists():
#                 messages.error(request, "Mobile number is already in use.")
#             else:
#                 # Create a new user
#                 user = User.objects.create_user(
#                     username=username, password=password, email=email
#                 )
#                 user.mobile_number = mobile_number  # Save the mobile number in the user model
#                 user.save()

#                 # Create a default profile for the user during signup
#                 profile_name = username
#                 profile = Profile(
#                     user=user, name=profile_name, mobile_number=mobile_number
#                 )
#                 profile.save()

#                 login(request, user)
#                 subject = "Signup Success"
#                 context = {"username": username}
#                 html_message = render_to_string("signup_success_email.html", context)
#                 plain_message = strip_tags(html_message)
#                 from_email = "realmdefend@gmail.com"
#                 to_email = user.email

#                 send_mail(
#                     subject,
#                     plain_message,
#                     from_email,
#                     [to_email],
#                     html_message=html_message,
#                 )
#                 return redirect("signin")
#         else:
#             # If the form is not valid, display the error messages
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field.capitalize()}: {error}")
#     else:
#         form = SignUpForm()

#     return render(request, "signup.html", {"form": form})

# #--------------------------------------------------------------------------------------------------------------------------


# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth.models import User

# def reset_password(request, token):
#     try:
#         user = User.objects.get(email='email')
#     except User.DoesNotExist:
#         error_message = "Invalid token or user not found."
#         return render(request, 'reset_password.html', {'error_message': error_message})

#     if default_token_generator.check_token(user, token):
#         if request.method == 'POST':
#             new_password = request.POST.get('new_password')
#             user.set_password(new_password)
#             user.save()
#             success_message = "Your password has been reset successfully."
#             return render(request, 'reset_password.html', {'success_message': success_message})

#         return render(request, 'reset_password.html', {'user': user})
#     else:
#         error_message = "Invalid token or user not found."
#         return render(request, 'reset_password.html', {'error_message': error_message})



# from django.core.mail import send_mail
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth.models import User

# def forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')  # Get the user's email from the form
        
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             error_message = "No user found with this email address."
#             return render(request, 'forgot_password.html', {'error_message': error_message})

#         token = default_token_generator.make_token(user)

#         reset_url = request.build_absolute_uri(reverse('resetpassword', args=[token]))

#         send_mail(
#             'Password Reset',
#             f'Click the link below to reset your password:\n{reset_url}',
#             'noreply@example.com',
#             [email],
#             fail_silently=False,
#         )

#         success_message = "An email with instructions to reset your password has been sent to your email address."
#         return render(request, 'forgot_password.html', {'success_message': success_message})

#     return render(request, 'forgot_password.html')


# views.py
# watchlist
# views.py

# from django.shortcuts import render, redirect
# from .models import Watchlist, Video
# from django.contrib.auth.decorators import login_required

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)  # Replace Video with your actual Video model
#     Watchlist.objects.get_or_create(user=request.user, video=video)
#     return redirect('movie_details', video_id=video_id)

# def video_detail(request, video_id):
#     video = get_object_or_404(Video, pk=video_id)
#     context = {'video': video}
#     return render(request, 'video_detail.html', context)
# @login_required
# def watchlist(request):
#     watchlist_items = Watchlist.objects.filter(user=request.user)
#     context = {'watchlist': watchlist_items}
#     return render(request, 'watchlist.html', context)




# from django.shortcuts import render, redirect
# from .models import Watchlist, Video, Profile
# from django.contrib.auth.decorators import login_required

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profile = Profile.objects.get(user=request.user)
#     Watchlist.objects.get_or_create(user=request.user, video=video, profile=profile)
#     return redirect('movie_details', video_id=video_id)


# from django.shortcuts import render, redirect
# from .models import Watchlist, Video, Profile
# from django.contrib.auth.decorators import login_required

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         profile = profiles.first()  # Choose the first profile if there are multiple profiles
#         Watchlist.objects.get_or_create(user=request.user, video=video, profile=profile)
#     else:
#         # Handle the case when no profile is found (This part depends on your application's logic)
#         pass
        
#     return redirect('movie_details', video_id=video_id)

# def watchlist_display(request):
#     user = request.user
#     videos = Video.objects.filter(watchlist__user=user)
#     context = {"videos": videos}
#     return render(request, "watchlist.html", context)


# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages

# @login_required
# def remove_from_watchlist(request):
#     if request.method == "POST":
#         video_id = request.POST.get("video_id")
#         try:
#             video = get_object_or_404(Video, pk=video_id)
#             Watchlist.objects.filter(user=request.user, video=video).delete()
#             messages.success(request, "Video removed from your watchlist.")
#         except Video.DoesNotExist:
#             messages.error(request, "Video not found.")
    
#     return redirect('watchlist_display')



from django.core.mail import send_mail


# views.py

import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import CustomUser  # Make sure to import your CustomUser model


def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = CustomUser.objects.get(email=email)
            otp = str(random.randint(100000, 999999))

            # Send OTP to the user's email (code for sending mail)
            subject = "Password Reset OTP"
            message = f"Your OTP for password reset: {otp}"
            from_email = "your-email@example.com"
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)

            request.session["reset_user_id"] = user.id
            request.session["reset_otp"] = otp

            return redirect("verify_otp")

        except CustomUser.DoesNotExist:
            error_message = "Email not found."
            return render(
                request, "forgot_password.html", {"error_message": error_message}
            )

    return render(request, "forgot_password.html")


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        expected_otp = request.session.get("reset_otp")

        if expected_otp is not None and entered_otp == expected_otp:
            # Clear OTP from session after successful verification
            del request.session["reset_otp"]
            return redirect("update_password")
            # return render(request, "update_password.html")
        else:
            error_message = "Invalid OTP."
            return render(request, "verify_otp.html", {"error_message": error_message})
    return render(request, "verify_otp.html")


def update_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        user_id = request.session.get("reset_user_id")

        try:
            user = CustomUser.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            del request.session["reset_user_id"]  # Clear user_id from session
            return render(request, "password_updated.html")
        except CustomUser.DoesNotExist:
            # Handle case where user is not found
            pass

    return render(request, "update_password.html")  # Redirect in case of errors


# Other views remain unchanged...


def password_updated(request):
    return render(request, "password_updated.html")

# from .models import ProfileWatchlist

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         for profile in profiles:
#             ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#     else:
#         # Handle the case when no profile is found (This part depends on your application's logic)
#         pass
        
#     return redirect('movie_details', video_id=video_id)


# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         # Existing user with profiles, use the existing profiles
#         for profile in profiles:
#             ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#     else:
#         # New user, create a new profile with profile ID starting from 1
#         last_profile = Profile.objects.order_by('-id').first()
#         new_profile_id = 1 if not last_profile else last_profile.id + 1
#         new_profile = Profile.objects.create(user=request.user, id=new_profile_id)
#         ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
        
#     return redirect('movie_details', video_id=video_id)

# from django.shortcuts import render, redirect
# from .models import Watchlist, Video, Profile
# from django.contrib.auth.decorators import login_required

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         for profile in profiles:
#             Watchlist.objects.get_or_create(user=request.user, video=video, profile=profile)
#     else:
#         # Handle the case when no profile is found (This part depends on your application's logic)
#         pass
        
#     return redirect('movie_details', video_id=video_id)


#####profilename and profile id saved in database####

# from django.contrib.auth.decorators import login_required
# from .models import Profile, ProfileWatchlist, Video

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         # Existing user with profiles, use the existing profiles
#         for profile in profiles:
#             ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#     else:
#         # New user, create a new profile (ID will start from 1 due to auto-increment)
#         new_profile = Profile.objects.create(user=request.user)
#         ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
        
#     return redirect('movie_details', video_id=video_id)


from django.contrib.auth.decorators import login_required
from .models import Profile, ProfileWatchlist, Video

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
    
#         # Existing user with profiles, use the existing profiles
#     for profile in profiles:
#         if profile.exists():
#             ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#         else:
#         # New user, create a new profile (ID will start from 1 due to auto-increment)
#             new_profile = Profile.objects.create(user=request.user)
#             ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
        
#         return redirect('movie_details', video_id=video_id)




from django.contrib.auth.decorators import login_required
from .models import Profile, ProfileWatchlist, Video
from django.shortcuts import redirect

# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profile_exists = Profile.objects.filter(user=request.user).exists()
#     for profile in profiles:
#     # Check if a profile exists for the user
#         if profile_exists:
#              profiles = Profile.objects.filter(user=request.user)
#         # Code before the for loop goes here (if needed)
#              ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#         # Code after the for loop goes here (if needed)
#         else:
#         # New user, create a new profile (ID will start from 1 due to auto-increment)
#              new_profile = Profile.objects.create(user=request.user)
#              ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
#         # Code after creating a new profile goes here (if needed)
    
#     # Code after the if-else block goes here (if needed)
#     return redirect('movie_details', video_id=video_id)

# from django.shortcuts import get_object_or_404, redirect
# from .models import Video, Profile, ProfileWatchlist

# def add_to_watchlist(request, profile_id, video_id):
#     # Get the video based on video_id
#     video = get_object_or_404(Video, pk=video_id)

#     # Get the specific profile based on profile_id and user
#     profile = get_object_or_404(Profile, pk=profile_id, user=request.user)

#     # Add the video to the profile's watchlist
#     ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)

#     # Redirect to the movie details page
#     return redirect('movie_details', video_id=video_id)


# @login_required
# def add_to_watchlist(request, video_id):
#     try:
#         video = Video.objects.get(pk=video_id)
#     except Video.DoesNotExist:
#         # Handle the case where the video doesn't exist
#         # You can return an error message or redirect to an error page
#         # Example: return HttpResponse("Video not found", status=404)
#         pass

#     profiles = Profile.objects.filter(user=request.user)

#     for profile in profiles:
#         # Create a ProfileWatchlist instance for each profile
#         ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)

#     return redirect('movie_details', video_id=video_id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Profile, ProfileWatchlist, Video

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if profiles.exists():
#         # Existing user with profiles, create the list of objects to add
#         profile_watchlist_objects = [
#             ProfileWatchlist(user=request.user, profile=profile, video=video)
#             for profile in profiles
#         ]
#         ProfileWatchlist.objects.bulk_create(profile_watchlist_objects)
#     else:
#         # New user, create a new profile (ID will start from 1 due to auto-increment)
#         new_profile = Profile.objects.create(user=request.user)
#         ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
        
#     return redirect('movie_details', video_id=video_id)



#### selecting the profile###############

from .models import Video, Profile, ProfileWatchlist
from django.shortcuts import render, redirect

# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user)
    
#     if request.method == 'POST':
#         selected_profile_id = request.POST.get('profile_id')
#         selected_profile = Profile.objects.get(id=selected_profile_id)
        
#         ProfileWatchlist.objects.get_or_create(user=request.user, profile=selected_profile, video=video)
        
#         return redirect('movie_details', video_id=video_id)

#     return render(request, 'add_to_watchlist.html', {'video': video, 'profiles': profiles})

# ############prifile nmae not svaaed###############3

# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
#     profiles = Profile.objects.filter(user=request.user, name="profile_name")  # Modify as needed
    
#     if profiles.exists():
#         # Existing user with profiles, use the existing profiles
#         for profile in profiles:
#             ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#     else:
#         # New user, create a new profile (ID will start from 1 due to auto-increment)
#         new_profile = Profile.objects.create(user=request.user)
#         ProfileWatchlist.objects.create(user=request.user, profile=new_profile, video=video)
    
#     return redirect('movie_details', video_id=video_id)




def add_to_watchlist(request, video_id):
    video = Video.objects.get(pk=video_id)
    profiles = Profile.objects.filter(user=request.user)

    
    # Check if a profile with the specified name exists for the user
    profile = Profile.objects.filter(user=request.user).first()
    
    if profile:
        # Existing user with a profile, use the existing profile
        ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
    else:
        # New user or user doesn't have a profile with the specified name, create a new profile
        new_profile = Profile.objects.create(user=request.user)
        ProfileWatchlist.objects.get_or_create(user=request.user, profile=new_profile, video=video)
    
    return redirect('movie_details', video_id=video_id)


# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from .models import Profile, ProfileWatchlist, Video

# # @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)
    
#     # Get the user's profile
#     profile = get_object_or_404(Profile, user=request.user)

#     # Save the video to the user's profile using the profile's name
#     ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
    
#     return redirect('movie_details', video_id=video_id)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from .models import Profile, ProfileWatchlist, Video

# @login_required
# def add_to_watchlist(request, video_id):
#     video = Video.objects.get(pk=video_id)

#     # Check if a profile with the specified name exists for the user
#     profile = Profile.objects.filter(user=request.user).first()

#     if profile:
#         # Existing user with a profile, use the existing profile
#         ProfileWatchlist.objects.get_or_create(user=request.user, profile=profile, video=video)
#     else:
#         # New user or user doesn't have a profile with the specified name, create a new profile
#         new_profile = Profile.objects.create(user=request.user)
#         ProfileWatchlist.objects.get_or_create(user=request.user, profile=new_profile, video=video)

#     return redirect('movie_details', video_id=video_id)






def hover_view(request):
    video_source = "static/videos/Kalki.mp4"  # Adjust the path to your video
    return render(request, 'hover.html', {'video_source': video_source})

def hover_player_view(request):
    video_src = request.GET.get('video_src', '')
    return render(request, 'hover_player.html', {'video_src': video_src})
