from django.urls import path
from apps.accounts import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registerUser_view, name='register_user'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    path('addresses/', views.my_addresses, name='my_addresses'),
    path('address/add/', views.add_address, name='add_address'),
    path(
        'addresses/<int:address_id>/edit/',
        views.edit_address,
        name='edit_address'
    ),
    path(
        'addresses/<int:address_id>/delete/',
        views.delete_address,
        name='delete_address'
    ),
    path(
        'addresses/<int:address_id>/default/',
        views.set_default_address,
        name='set_default_address'
    ),

    path("test-error/", views.test_error)
]



if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )