from django.shortcuts import render,redirect
from .forms import UserSignupForm
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import Account
from django.contrib import messages

# Create your views here.
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
            return redirect('signup')
    else:
        form = UserSignupForm()
    context = {
        "form": form
    }
    return render(request, 'userauths/signup.html', context)

# def signup(request):
#     if request.method == "POST":
#         form  = UserSignupForm(request.POST)
#         if form.is_valid():
#             new_user = form.save(commit=False)
#             new_user.username = form.cleaned_date['email']
#             new_user.save()
#             print('User registered')
#             username = form.cleaned_data.get('email')
#             messages.success(request,f'User {username} was Created')
#             new_user  = authenticate(username=form.cleaned_data['email'],password = form.cleaned_data.get('password1'))
#             if new_user is not None:
#                 login(request,new_user)
#                 return redirect('core:index')
#             else:
#                 messages.error(request,'Authentication failed. Please Try again.')
#                 return redirect('signup')
                
#         else:
#             print(form.errors)
        
#     else:
#         form  = UserSignupForm()
#         print('User Cannot be registered')
    
#     context = {
#         "form" : form
#     }
#     return render(request,'userauths/signup.html',context)