from django.utils import timezone
from base.base_models import BaseModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django_resized import ResizedImageField

class UserManager(BaseUserManager):

    def create_superuser(self,phone,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(phone,password,**extra_fields)
        return user


    def create_user(self,phone,password=None,**extra_fields):

        if not phone :
            raise ValueError('Phone must not be null.')

        user = self.model(
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser,PermissionsMixin):

    phone = models.CharField(
        max_length=11,
        unique=True,
    )
    first_name = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
    )
    photo = ResizedImageField(
        upload_to='users/photo/',
        size=[500, 500],
        crop = ['center','middle'] ,
        quality=100,
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name :
            return self.first_name
        elif self.last_name :
            return self.last_name
        else :
            return ""

