from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Profile → OneToOne → User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullName = models.CharField(max_length=20)
    phone = models.IntegerField(default=0)
    address = models.CharField(max_length=100)
    profileImage = models.ImageField(upload_to='profiles/')

    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)


    def __str__(self):
        return self.fullName

