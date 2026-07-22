from django.urls import path

from . import views


urlpatterns = [
    path("policies/", views.policy_list),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
    path("auth/me/", views.me),
    path("profiles/me/", views.profile_me),
]
