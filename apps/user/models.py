from datetime import timedelta
from utils.code import create_code
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django_resized import ResizedImageField
from utils.validate import check_phone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(phone, password, **extra_fields)
        return user

    def create_user(self, phone, password=None, **extra_fields):

        if not phone:
            raise ValueError('Phone must not be null.')

        success, message = check_phone(phone)
        if not success:
            raise ValueError(message)

        user = self.model(
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user


class OTPManager(models.Manager):
    def create_code(self,phone):

        if not self.filter(phone=phone).exists():
            opt = self.create(phone=phone)

        else:
            opt = self.get(phone=phone)
            if not opt.is_active :
                #delete and make it again
                opt.delete()
                opt = self.create(phone=phone)

            else:
                raise ValueError('Code already exists.')

        return opt


    def check_code(self, phone, code):
        if not self.filter(phone=phone).exists():
            raise ValueError('Phone Number or Code does not exist.')

        opt = self.get(phone=phone)

        if not opt.is_active:
            raise ValueError('Code is expired.')

        if code != opt.code:
            raise ValueError('Code does not match.')

        # remove_code
        opt.delete()
        return True

    def time_to_be_expired(self, phone):
        if not self.filter(phone=phone).exists():
            raise ValueError('Phone Number does not exist.')

        opt = self.get(phone=phone)

        if not opt.is_active:
            return timedelta(minutes=0)

        return timezone.now() - opt.created_at + timedelta(minutes=2)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(
        max_length=11,
        unique=True,
        verbose_name=_('Phone'),
    )
    first_name = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_('First Name'),
    )
    last_name = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_('Last Name'),
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email'),
    )
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Bio')
    )
    photo = ResizedImageField(
        upload_to='users/photo/',
        size=[500, 500],
        crop=['middle', 'center'],
        quality=100,
        null=True,
        blank=True,
        verbose_name=_('Photo'),
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Date Joined'),
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Is Admin'),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return ""


class Marketer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )

    def __str__(self):
        return self.user.phone


class OTP(models.Model):
    phone = models.CharField(
        max_length=11,
        verbose_name=_('Phone Number'),
        unique=True,
    )
    code = models.CharField(
        max_length=6,
        default=create_code,
        verbose_name=_('Code'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    objects = models.Manager()
    codes = OTPManager()

    @property
    def is_active(self):
        return timezone.now() < self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"{self.phone} : {self.code}"
