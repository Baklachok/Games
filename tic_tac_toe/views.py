from django.shortcuts import render

def index(request):
    return render(request, 'base.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'registration.html')
