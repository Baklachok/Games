from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from tic_tac_toe.models import GameStats, Game


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

def start_game(request):
    # Создание новой игры и отправка ID игры на клиент
    current_user = request.user
    game = Game.objects.create(player1=current_user, player2=None)
    return JsonResponse({'game_id': game.id})

def game_state(request, game_id):
    # Получение состояния игры по ID
    game = Game.objects.get(id=game_id)
    # Формирование данных об игре для отправки на клиент
    game_data = {...}
    return JsonResponse(game_data)

@login_required
def join_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, is_active=True, player2__isnull=True)
    game.player2 = request.user
    game.save()
    return redirect('play_game', game_id=game_id)

@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    # Дополнительная логика для отображения игрового поля и обработки ходов
    context = {'game': game}
    return render(request, 'play_with_human.html', context)

def play_with_human(request):
    return render(request, 'active_games.html')

def create_game(request):
    # Создаем новую игру
    new_game = Game.objects.create(board='', player1=request.user, player2=None, is_active=True)

    # Получаем ID созданной игры
    game_id = new_game.id

    # Возвращаем ответ с ID созданной игры
    return JsonResponse({'game_id': game_id})
