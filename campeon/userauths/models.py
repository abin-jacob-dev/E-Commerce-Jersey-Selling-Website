from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import random,string

class MyAccountManager(BaseUserManager):
    def create_user(self, full_name, username, email, password=None):
        if not email:
            raise ValueError("User must have an Email Address")
        if not username:
            raise ValueError("User must have an username")
        user = self.model(
            email=self.normalize_email(email), username=username, full_name=full_name
        )
        user.set_password(password)
        user.save()  # save(using = (db name)_db) -> to change the db
        return user

    def create_superuser(self, full_name, username, email, password):
        user = self.create_user(
            full_name=full_name,
            username=username,
            password=password,
            email=self.normalize_email(email),
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_superadmin = True
        user.save()
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    username = models.CharField(max_length=250, unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )
    referral_code = models.CharField(max_length=8, null=True, blank=True,unique=True)
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )
    referral_count = models.PositiveIntegerField(default=0)
    total_referral_amount = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    objects = MyAccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    @staticmethod
    def create_referral_code():
        chars = string.ascii_uppercase+string.digits
        while True:

            referral_code = "".join(random.choices(chars,k=8))
            if not Account.objects.filter(referral_code = referral_code).exists():
                return referral_code
            
    def save(self,*args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.create_referral_code()
        super().save(*args, **kwargs)

    

    def __str__(self):
        return self.email
    

