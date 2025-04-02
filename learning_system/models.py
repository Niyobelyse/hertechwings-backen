from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from uuid import uuid4
from django.conf import settings
from django.forms import ValidationError
from django.utils.timezone import now
from django.utils import timezone 


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set properly")
        if not first_name or not last_name:
            raise ValueError("First name and last name are required")
        if not phone:
            raise ValueError("Phone number is required")
        if not password:
            raise ValueError("Password is required")
        if role not in User.UserRoleChoices.values:
            raise ValueError("Invalid user role")
        
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, phone=phone, role=role, **extra_fields
        )
        user.set_password(password)  
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class UserRoleChoices(models.TextChoices):
        STUDENT = "student", "Student"
        MENTOR = "mentor", "Mentor"


    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=UserRoleChoices.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'password', 'role']

    objects = UserManager()

    def __str__(self):
        return self.email


class OTP(models.Model):
    EMAIL_VALIDATION = "EMAIL_VALIDATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    
    OTP_TYPE_CHOICES = [
        (EMAIL_VALIDATION, "Email Validation"),
        (PASSWORD_RESET, "Password Reset"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() <= self.created_at + settings.VERIFICATION_CODE_EXPIRY
    

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.ImageField(upload_to="uploads/")
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title






class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    available_date = models.DateTimeField()
    due_date = models.DateTimeField()
    points = models.IntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.due_date.tzinfo:
            self.due_date = timezone.make_aware(self.due_date)
        if not self.available_date.tzinfo:
            self.available_date = timezone.make_aware(self.available_date)
        super().save(*args, **kwargs)




class CourseResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("link", "Link"),
        ("file", "File")
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="resources")
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True) 
    file = models.FileField(upload_to="uploads/", blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

