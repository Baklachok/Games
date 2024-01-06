from django.urls import path

from tic_tac_toe import views

urlpatterns = [
    path("", views.index, name="index"),
    path("log_in/", views.login, name="log_in"),
    path("sign_up", views.signup, name="sign_up"),
]