from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class MyAccountManager(BaseUserManager):
    def create_user(self, full_name, username, email, password):
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
    phone_number = models.CharField(max_length=50)
    referral_code = models.CharField( max_length=50,null = True,blank=True)
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    objects = MyAccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    def __str__(self):
        return self.email
