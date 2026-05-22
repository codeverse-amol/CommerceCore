from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.forms import ProfileForm, UserForm
from apps.accounts.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.



def registerUser_view(request):
    form = UserForm()
    if request.method=="POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user)            # user automatically logged in
            return redirect('/')            # redirected to dashboard/home

    return render(request, "accounts/register.html", {'form':form})

# This view function, register_user, handles the creation of new user accounts. It checks if the request method is POST, and if so, it processes the submitted form data. If the form is valid, it creates a new user object, sets the password using Django's set_password method (which hashes the password), and saves the user to the database. After successful creation, it redirects to the 'new_user' view. If the request method is not POST, it renders an empty user creation form.
def new_user(request):
    users = User.objects.all()
    return render(request, "registration/new_user.html", {'users':users})




# LOGIN VIEW
# The login_view function handles user authentication. It checks if the request method is POST, retrieves the username and password from the request, and uses Django's authenticate function to verify the credentials. If authentication is successful, it logs the user in and redirects them to the dashboard. If authentication fails, it returns an error message. If the request method is not POST, it renders the login page.
def login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user =  form.get_user()
            login(request, user)
            return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})







@login_required
def index(request):
    return render(request, "accounts/index.html")






@login_required
def create_profile(request):
    if request.method=="POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            # Associate the profile with the currently logged-in user
            profile.user = request.user
            profile.save()
            return redirect('homepage')
    else:
        form = ProfileForm()
    return render(request, "accounts/create_profile.html", {'form':form})


@login_required
def user_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, "accounts/profile.html", {'profile': profile})

# LOGOUT VIEW
@login_required 
def logout_view(request):

    # DESTROY SESSION
    # request.session.flush()
    logout(request)            # Django's built-in logout function also clears the session data

    return redirect('login')

