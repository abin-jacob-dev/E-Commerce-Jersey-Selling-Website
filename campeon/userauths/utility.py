from django.db import models
from userauths.models import Account
import random
from datetime import datetime, timedelta
import string
from django.utils import timezone


class OTP(models.Model):
    email = models.EmailField(max_length=254)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now())

    def is_expired(self):
        return timezone.now() > self.expires_at

    def generate_otp(self):
       
        self.otp = "".join(random.choices(string.digits, k=6))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()

    def send_otp_email(self,email):
        from django.core.mail import send_mail

        subject = "Your OTP for Account Creation"
        message = f"Your OTP for creating your profile is {self.otp}.It is valid for 5 minutes"
        try:
            send_mail(subject, message, "abinjacobsmtp@gmail.com", [email])
            print("Email sent from the server")
        except Exception as e:
            print(f"Error sending email : {e}")
