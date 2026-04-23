from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request,"core/home.html")
def shop(request):
    return render(request,"core/shop.html")
def contact(request):
    return render(request,"core/contact.html")
def about(request):
    return render(request,"core/about.html")
