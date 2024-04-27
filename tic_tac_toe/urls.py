from django.urls import path

from tic_tac_toe import views, consumers

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("sign_up", views.signup, name="sign_up"),
    path("logout", views.log_out, name="logout"),
    path("tic-tae-toe/", views.tic_tae_toe, name="tic-tae-toe"),
    # path("play-with-human/", views.play_with_human, name="play-with-human"),
    path('update_stats/', views.update_stats, name='update_stats'),
    path('get_stats/', views.get_stats, name='get_stats'),
    path('all_stats/', views.all_stats, name='all_stats'),
    path("join-game/<int:game_id>/", views.join_game, name="join_game"),
    path("play-game/<int:game_id>/", views.play_game, name="play_game"),
    path("play-with-human/", views.play_with_human, name="play-with-human"),
    path("create-game/", views.create_game, name="create_game"),
    # Websocket URL pattern for the game consumer
    path("ws/play-game/<int:game_id>/", consumers.GameConsumer.as_asgi()),
]