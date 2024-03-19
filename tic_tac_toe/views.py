from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from tic_tac_toe.models import GameStats


def index(request):
    board = ['X', 'O', 'X', 'O', 'X', 'X', 'O', '', 'O']

    context = {'board': board}
    return render(request, 'index.html', context)

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

@login_required
def tic_tae_toe(request):
    board = ['', '', '', '', '', '', '', '', '']

    context = {'board': board}

    return render(request, 'tic-tae-toe.html', context)

def play_with_human(request):
    board = ['', '', '', '', '', '', '', '', '']

    context = {'board': board}
    return render(request, 'play_with_human.html', context)

@csrf_exempt
@login_required
def update_stats(request):
    result = request.GET.get('result', None)

    if result:
        stats, created = GameStats.objects.get_or_create(user=request.user)

        if result == 'win':
            stats.wins += 1
        elif result == 'loss':
            stats.losses += 1

        stats.save()

    return HttpResponse(status=200)

@login_required
def get_stats(request):
    stats = GameStats.objects.get(user=request.user)
    data = {'wins': stats.wins, 'losses': stats.losses}
    return JsonResponse(data)

def all_stats(request):
    # Получаем все объекты GameStats из базы данных
    all_stats = GameStats.objects.all()

    # Передаем данные в шаблон для отображения
    context = {'all_stats': all_stats, 'user': request.user}
    return render(request, 'all_stats.html', context)
