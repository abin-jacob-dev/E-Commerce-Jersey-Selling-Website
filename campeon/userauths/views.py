from django.shortcuts import render,redirect
from .forms import UserSignupForm
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import Account
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def dashboard(request):
    return render(request,'userauths/dashboard.html')
def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
            email = form.cleaned_data.get('email')
            username = email.split('@')[0]
            password = form.cleaned_data.get('password')
            referral_code = form.cleaned_data.get('referral_code')
            user=Account.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                username=username
            )
            user.referral_code = referral_code
            user.save()
            messages.success(request,'Registeration Successful')
            return redirect('userauths:signup')
    else:
        form = UserSignupForm()
    context = {
        "form": form
    }
    return render(request, 'userauths/signup.html', context)

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        user = authenticate(email=email,password=password)
        print(user)
        if user is None:
            messages.error(request,'Invalid Credentials')
            print('user is none')
            return redirect('userauths:signin')
        if user.is_blocked:
            messages.error(request,'Your acccount has been blocked')
            print('user blocked')
            return redirect('userauths:signin')

        login(request,user)
        print('user logged in')
        messages.success(request,'User Logged In')
        if user.is_staff or user.role =='admin':
            return redirect('userauths:dashboard')
        
        return redirect('userauths:dashboard')
    return render(request,'userauths/signin.html')
@login_required(login_url = '/login/')
def signout(request):
    logout(request)
    messages.success(request,'You have Signed Out!')
    return redirect('signin')