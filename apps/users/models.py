import os 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.utils.translation import gettext_lazy as _
#from company.models import Company
from django.urls import reverse
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
#from members.models import Course


# class TimeStampMixin(models.Model):
#     created_at = models.DateTimeField(default=datetime.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        #extra_fields['company'] = None
        
        return self.create_user(email, password, **extra_fields)


class User(TimeStampedModel,AbstractBaseUser, PermissionsMixin):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
    #ompany = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    #course = models.ManyToManyField(Course, related_name='staff')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_company_owner = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    date_of_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=15, unique=True,null=True, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.OTHER,
    )
    #membership_date = models.DateField(auto_now_add=True)
    first_login = models.BooleanField(default=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_course_as_string(self):
        return ", ".join(course.title for course in self.course.all())
    
    def get_absolute_url(self):
        return reverse('user_edit', args=[str(self.id)])
    
    def get_absolute_url_delete(self):
        return reverse('user_delete', args=[str(self.id)])

    def get_absolute_url_dashboard(self):
        return reverse('user_dashboard', args=[str(self.id)])
