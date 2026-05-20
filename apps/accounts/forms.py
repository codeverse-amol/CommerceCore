from django import forms
from apps.accounts.models import Profile
from django.contrib.auth.models import User


# Create User via Form (No login system)
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']




class ProfileForm(forms.ModelForm):
#     user = forms.ModelChoiceField(
#     queryset=User.objects.all(),
#     empty_label="Select User"   # removes "--------"
# )

    class Meta:
        model = Profile
        fields = "__all__"


# User → Django View → ORM → SQL → MySQL → Data → ORM → View → Template