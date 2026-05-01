from django.db import models
from userauths.models import Account
import random
from datetime import datetime, timedelta
import string
from django.utils import timezone
import re
from django.conf import settings


class OTP(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
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

        subject = "Your OTP for Profile Update"
        message = f"""
        Hello,

        We received a request to update your profile.

        Your One-Time Password (OTP) is: {self.otp}

        ⏳ This OTP is valid for 5 minutes.
        🔒 Do not share this OTP with anyone for security reasons.

        If you did not request this change, please ignore this email or contact our support team immediately.

        Thank you,  
        Your Support Team
        """
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            print("Email sent from the server")
        except Exception as e:
            print(f"Error sending email : {e}")


def validate_password(password):

    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one number"
    if not re.search(r"[@$!%*?&]", password):
        return "Password must contain at least one special character"
    return None


def validate_name(name):
    if re.search(r"\d", name):
        return "Name should not contain numbers"
    return None
