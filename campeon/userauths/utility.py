from django.db import models
from userauths.models import Account
import random
from datetime import datetime, timedelta
import string
from django.utils import timezone
from django.conf import settings


class OTP(models.Model):
    email = models.EmailField(max_length=254)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def generate_otp(self):
        self.otp = "".join(random.choices(string.digits, k=6))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()

    def send_otp_email(self, email):
        from django.core.mail import send_mail

        subject = "Verify Your Campeon Account - OTP"
        message = f"""
        Hello,

        Thank you for signing up with Campeon.

        Your One-Time Password (OTP) for account verification is:

        
         {self.otp}

         
        This OTP is valid for 5 minutes. Please do not share this code with anyone.

        If you did not attempt to create an account, you can safely ignore this email.

        Welcome aboard!  
        Team Campeon
        """

        try:
            send_mail(
                subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False
            )
            print("Email sent from the server")
        except Exception as e:
            print(f"Error sending email : {e}")
