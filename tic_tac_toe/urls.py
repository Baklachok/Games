from django.urls import path

from tic_tac_toe import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("sign_up", views.signup, name="sign_up"),
    path("logout", views.log_out, name="logout"),
    path("tic-tae-toe/", views.tic_tae_toe, name="tic-tae-toe"),
    path('update_stats/', views.update_stats, name='update_stats'),
    path('get_stats/', views.get_stats, name='get_stats'),
]