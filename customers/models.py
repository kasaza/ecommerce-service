from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email
