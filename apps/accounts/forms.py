from django import forms
from apps.accounts.models import Profile, Address
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))




class ProfileForm(forms.ModelForm):
#     user = forms.ModelChoiceField(
#     queryset=User.objects.all(),
#     empty_label="Select User"   # removes "--------"
# )

    class Meta:
        model = Profile
        # fields = "__all__"
        exclude = ['user']





class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        exclude = ['user']




# User → Django View → ORM → SQL → MySQL → Data → ORM → View → Template