from django.shortcuts import render, redirect

# Create your views here.


# Landing page view
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'main/landing.html')