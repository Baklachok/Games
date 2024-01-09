from django.urls import path

from tic_tac_toe import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("sign_up", views.signup, name="sign_up"),
    path("logout", views.log_out, name="logout"),
]