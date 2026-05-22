from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.


# Landing page view
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'main/landing.html')





# DASHBOARD VIEW

@login_required          # This decorator ensures that only authenticated users can access the dashboard view. If a user is not authenticated, they will be redirected to the login page.
def dashboard_view(request):
    # user = get_active_user(request)
    return render(request, 'main/dashboard.html')



# get_active_user function checks if the user is authenticated and returns the user object. If the user is not authenticated, it returns the last created user from the database. This function can be used to retrieve the active user in various views.
# def get_active_user(request):
#     if request.user.is_authenticated:
#         print("Logged in")
#         return request.user
#     return None