from django.urls import path
from apps.main import views


urlpatterns = [
    path('', views.landing_page, name='landing_page'),

]