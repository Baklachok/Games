from django.db import models
from django.contrib.auth.models import User

class GameStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

class Game(models.Model):
    board = models.CharField(max_length=9)  # строка для хранения состояния доски
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player2', null=True, blank = True)
    is_active = models.BooleanField(default=True)  # Показывает активна ли игра
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_current_player',
                                       null=True, blank=True)

    class Meta:
        db_table = 'tic_tac_toe_game'  # Имя таблицы в базе данных

class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
