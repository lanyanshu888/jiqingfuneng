from django.contrib import admin

from .models import (
    Activity,
    AuthToken,
    Course,
    CourseProgress,
    Enrollment,
    Favorite,
    GrowthEvent,
    Mentor,
    MentorConsultation,
    Opportunity,
    Policy,
    ReviewItem,
    YouthProfile,
)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "created_at")
    search_fields = ("user__username", "key")


@admin.register(YouthProfile)
class YouthProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "region", "profile_type", "updated_at")
    search_fields = ("user__username", "nickname", "region", "profile_type")


@admin.register(Policy, Opportunity, Course, Activity, Mentor)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("title",)
    list_editable = ("status",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "activity", "opportunity", "created_at")
    search_fields = ("user__username", "activity__title", "opportunity__title")


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "completed", "completed_at")
    list_filter = ("completed",)


@admin.register(MentorConsultation)
class MentorConsultationAdmin(admin.ModelAdmin):
    list_display = ("user", "mentor", "status", "scheduled_at", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "mentor__title", "question")


admin.site.register(Favorite)
admin.site.register(GrowthEvent)
admin.site.register(ReviewItem)
