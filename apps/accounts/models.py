from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Profile → OneToOne → User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullName = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    profileImage = models.ImageField(upload_to='profiles/')

    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1)


    def __str__(self):
        return self.fullName



class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    full_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    address_line = models.CharField(max_length=255)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"