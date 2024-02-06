from django.contrib import admin

from tic_tac_toe.models import GameStats


@admin.register(GameStats)
class GameStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'wins', 'losses')
