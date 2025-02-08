from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='user')
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # ✅ Added phone_number field
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # ✅ Fixed BooleanField default

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'account_type', 'country', 'state', 'phone_number', 'address']  # ✅ Aligned with model

    def __str__(self):
        return self.email

