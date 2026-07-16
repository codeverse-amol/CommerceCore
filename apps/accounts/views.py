from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.forms import ProfileForm, UserForm, AddressForm
from apps.accounts.models import Profile, Address
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


# LOGOUT VIEW
@login_required 
def logout_view(request):

    # DESTROY SESSION
    # request.session.flush()
    logout(request)            # Django's built-in logout function also clears the session data

    return redirect('login')




@login_required
def create_profile(request):

    if hasattr(request.user, 'profile'):
        return redirect('profile')
    
    if request.method=="POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            # Associate the profile with the currently logged-in user
            profile.user = request.user
            profile.save()
            return redirect('profile')
    else:
        form = ProfileForm()
    return render(request, "accounts/create_profile.html", {'form':form})




@login_required
def profile_view(request):

    if not hasattr(request.user, 'profile'):
        return redirect('create_profile')
    
    profile = request.user.profile

    return render(request, "accounts/profile.html", {'profile': profile})



@login_required
def edit_profile(request):

    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        
    return render(request, "accounts/edit_profile.html", {'profile': profile, 'form': form})


@login_required
def add_address(request):

    address = Address.objects.all()

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            # first address automatically default
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True

            address.save()

            return redirect('my_addresses')
        

    else:
        form = AddressForm()

    
    return render(request, 'accounts/add_address.html', {'form': form})



@login_required
def my_addresses(request):

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'accounts/my_addresses.html', {'addresses': addresses})



@login_required
def edit_address(request, address_id):

    address = get_object_or_404(Address, user=request.user, id=address_id)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()

            return redirect('my_addresses')
        
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/edit_address.html', {'form': form})



@login_required
def delete_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        address.delete()

        return redirect('my_addresses')

    return render(
        request,
        'accounts/delete_address.html',
        {'address': address}
    )



@login_required
def set_default_address(request, address_id):

    Address.objects.filter(
        user=request.user
    ).update(
        is_default=False
    )

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    address.is_default = True
    address.save()

    return redirect('my_addresses')








def test_error(request):
    1 / 0
