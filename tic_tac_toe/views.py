from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # Аутентификация пользователя
            login(request, form.get_user())
            return redirect('index')
        else:
            return render(request, 'login.html', {'error_message': 'Введены неверные данные'})

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        # Проверяем уникальность имени пользователя
        if User.objects.filter(username=username).exists():
            return render(request, 'registration.html', {'error_message': 'Пользователь с таким именем уже существует'})

        if password == confirm_password:
            # Создаем нового пользователя
            user = User.objects.create_user(username=username, password=password)
            # Аутентифицируем пользователя сразу после регистрации
            login(request, user)
            return redirect('index')
        else:
            # Обработка ошибки, если пароли не совпадают
            return render(request, 'registration.html', {'error_message': 'Пароли не совпадают'})

    return render(request, 'registration.html')

def log_out(request):
    logout(request)
    return redirect('index')
