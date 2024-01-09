from django.contrib.auth import logout
from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'registration.html')

def log_out(request):
    logout(request)
    return redirect('index')
