1. Create an OTP Model

You will need a model to store the OTP, its expiration time, and the user it belongs to. This way, you can verify if the OTP is correct and still valid.

from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # OTP will be 6 digits
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return datetime.now() > self.expires_at

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # 6-digit OTP
        self.expires_at = datetime.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
        self.save()

    def send_otp_email(self):
        # You can use Django's EmailMessage or send_mail function to send the OTP to the user's email.
        from django.core.mail import send_mail
        subject = "Your OTP for Profile Update"
        message = f"Your OTP for updating your profile is {self.otp}. It is valid for 5 minutes."
        send_mail(subject, message, 'noreply@yourdomain.com', [self.user.email])
2. Update Your Views to Handle OTP

Now, let's modify the edit_profile view to generate and send an OTP when the user attempts to edit their profile. This involves two stages:

Stage 1: Send OTP to email.
Stage 2: Allow the user to input the OTP and verify it.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import OTP
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Stage 1: User wants to initiate OTP process
        otp = OTP.objects.filter(user=request.user, otp=request.POST.get('otp', '')).first()

        if 'send_otp' in request.POST:  # Step to send OTP
            # Generate OTP and send it to the user's email
            otp = OTP.objects.create(user=request.user)
            otp.generate_otp()
            otp.send_otp_email()

            messages.info(request, 'OTP has been sent to your email.')
            return redirect('user:edit_profile')  # Redirect to the same page to input OTP

        # Stage 2: Verify OTP
        elif otp and otp.otp == request.POST.get('otp', '') and not otp.is_expired():
            # OTP is valid
            full_name = request.POST.get('full_name', '')
            email = request.POST.get('email', '')
            phone_number = request.POST.get('phone_number', '')

            # Update the user details
            request.user.full_name = full_name
            request.user.email = email
            request.user.phone_number = phone_number
            request.user.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user:profile')
        
        elif otp and otp.is_expired():
            messages.error(request, 'Your OTP has expired. Please request a new one.')
            return redirect('user:edit_profile')

        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, "user/edit_profile.html")
3. Add OTP Field in the Template

Now, modify your template (edit_profile.html) to show the OTP field and allow the user to request a new OTP if needed.

{% extends 'user/partials/base.html' %}
{% load static %}
{% block content %}
  <main class="flex-1 bg-lime-light p-12">
    <div class="flex justify-between items-center mb-12">
      <h2 class="text-6xl font-black uppercase tracking-tighter leading-none tracking-tightest">EDIT PROFILE</h2>
      <a href="{% url "user:profile" %}" class="text-[10px] font-black uppercase tracking-widest hover:underline transition-all">Back to Profile</a>
    </div>

    <form class="max-w-4xl space-y-12" method="POST">
      {% csrf_token %}
      <!-- Avatar Upload Section (unchanged) -->

      <!-- OTP Section -->
      <div class="flex items-center gap-10">
        <div>
          <h4 class="text-sm font-black uppercase tracking-widest mb-2 tracking-tightest">Enter OTP</h4>
          <p class="text-[9px] font-bold text-black-300 uppercase tracking-widest leading-loose">
            Please check your email for the OTP.
          </p>
          <input name="otp" type="text" class="w-full bg-gray-50 border border-gray-100 rounded-lg px-6 py-4 text-xs font-black uppercase tracking-widest focus:outline-none focus:ring-2 focus:ring-lime/20" />
        </div>
      </div>

      <!-- Form Fields (Full Name, Email, Phone) -->
      <div class="bg-white p-12 rounded-sm shadow-sm">
        <div class="grid grid-cols-2 gap-10">
          <!-- Full Name, Email, Phone Number Fields (same as before) -->
        </div>

        <div class="flex items-center gap-4 pt-12 border-t border-gray-50 mt-12">
          <!-- Save Changes Button (only visible after OTP is verified) -->
          <button type="submit" name="save_changes" class="bg-lime-dark text-white px-12 py-5 text-[10px] font-black uppercase tracking-[0.2em] rounded-sm shadow-xl hover:bg-black transition-all">Save Changes</button>
          <button type="submit" name="send_otp" class="bg-lime-dark text-white px-12 py-5 text-[10px] font-black uppercase tracking-[0.2em] rounded-sm shadow-xl hover:bg-black transition-all">Send OTP</button>
        </div>
      </div>
    </form>
  </main>
{% endblock %}
Explanation:
OTP Generation and Email: When the user presses "Send OTP", the OTP is generated, saved in the database, and sent to the user's email.
OTP Timer: The OTP is set to expire after 5 minutes. The is_expired method checks if the OTP has expired.
Verify OTP: The user must enter the OTP to unlock the profile fields and make changes. If the OTP is correct and valid, the changes are saved.
Considerations:
Security: Ensure your email