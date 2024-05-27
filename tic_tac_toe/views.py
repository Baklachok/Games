import logging

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from tic_tac_toe.models import GameStats, Game, Move


logger = logging.getLogger(__name__)

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
    try:
        # Получаем состояние доски из объекта игры
        game = Game.objects.get(id=game_id)
        board = game.board

        # Получаем все ходы для данной игры
        moves = Move.objects.filter(game=game)
        moves_list = [{'player': move.player.username, 'position': move.position} for move in moves]

        # Возвращаем состояние игры в формате JSON
        return JsonResponse({'board': board, 'moves': moves_list})
    except Game.DoesNotExist:
        # Если игра с указанным ID не найдена, возвращаем ошибку 404
        return JsonResponse({'error': 'Game not found'}, status=404)

@login_required
def join_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    current_user = request.user

    if game.player2 is None and current_user != game.player1:
        game.player2 = current_user
        game.save()

    return redirect('play_game', game_id=game_id)

@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    current_user = request.user

    board = ['', '', '', '', '', '', '', '', '']

    context = {'game': game, 'user': current_user, 'board': board}
    return render(request, 'play_with_human.html', context)

@login_required
def create_game(request):
    if request.method == 'POST':
        try:
            # Создаем новую игру
            new_game = Game.objects.create(board=' ' * 9, player1=request.user, is_active=True,
                                           current_player=request.user)
            # Получаем ID созданной игры
            game_id = new_game.id
            # Возвращаем ответ с ID созданной игры
            return JsonResponse({'game_id': game_id})
        except Exception as e:
            logger.error("Ошибка при создании игры: %s", str(e))
            return JsonResponse({'error': 'Ошибка при создании игры'}, status=500)
    else:
        logger.warning("Недопустимый метод запроса: %s", request.method)
        return HttpResponse(status=405)

@login_required
def play_with_human(request):
    try:
        active_games = Game.objects.filter(is_active=True)
        logger.debug("Найдено %d активных игр", active_games.count())
        for game in active_games:
            logger.debug("Игра ID: %d, Игрок 1: %s, Игрок 2: %s", game.id, game.player1.username, game.player2.username if game.player2 else 'None')
        return render(request, 'active_games.html', {'active_games': active_games})
    except Exception as e:
        logger.error("Ошибка при получении активных игр: %s", str(e))
        return JsonResponse({'error': 'Ошибка при получении активных игр'}, status=500)


@csrf_exempt
@login_required
def update_game(request):
    if request.method == 'POST':
        position = request.POST.get('position')
        game_id = request.POST.get('game_id')
        current_player = request.user

        if position is not None and game_id is not None:
            try:
                # Получаем игру из базы данных
                game = Game.objects.get(id=game_id)

                # Создаем объект хода и сохраняем его в базе данных
                move = Move.objects.create(game=game, player=current_player, position=position)

                # Обновляем состояние доски игры
                game.board = request.POST.get('board')
                game.current_player = game.player1 if current_player == game.player2 else game.player2
                game.save()

                return HttpResponse(status=200)
            except Game.DoesNotExist:
                return JsonResponse({'error': 'Game not found'}, status=404)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)

