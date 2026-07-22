from django.urls import path

from . import agent_views, views


urlpatterns = [
    path("agent/binding-code/", agent_views.create_binding_code),
    path("agent/bind/", agent_views.bind_account),
    path("agent/skills/profile-context/", agent_views.profile_context),
    path("agent/skills/policy-search/", agent_views.policy_search),
    path("agent/skills/resource-match/", agent_views.resource_match),
    path("agent/skills/career-plan/", agent_views.career_plan),
    path("policies/", views.policy_list),
    path("policies/<int:policy_id>/", views.policy_detail),
    path("opportunities/", views.opportunity_list),
    path("opportunities/<int:opportunity_id>/", views.opportunity_detail),
    path("opportunities/<int:opportunity_id>/enroll/", views.enroll_opportunity),
    path("courses/", views.course_list),
    path("courses/<int:course_id>/", views.course_detail),
    path("courses/<int:course_id>/complete/", views.complete_course),
    path("activities/", views.activity_list),
    path("activities/<int:activity_id>/", views.activity_detail),
    path("activities/<int:activity_id>/enroll/", views.enroll_activity),
    path("me/growth/", views.growth_records),
    path("recommendations/", views.recommendations),
    path("favorites/toggle/", views.toggle_favorite),
    path("mentors/", views.mentor_list),
    path("mentors/<int:mentor_id>/consult/", views.consult_mentor),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
    path("auth/me/", views.me),
    path("profiles/me/", views.profile_me),
]
