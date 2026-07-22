from django.urls import path

from . import views


urlpatterns = [
    path("policies/", views.policy_list),
    path("opportunities/", views.opportunity_list),
    path("courses/", views.course_list),
    path("activities/", views.activity_list),
    path("activities/<int:activity_id>/enroll/", views.enroll_activity),
    path("mentors/", views.mentor_list),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
    path("auth/me/", views.me),
    path("profiles/me/", views.profile_me),
]
