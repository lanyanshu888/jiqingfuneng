from django.contrib import admin

from .models import (
    Activity,
    AgentBindingCode,
    AgentConversation,
    AgentMessage,
    AgentToolLog,
    AgentUserBinding,
    AuthToken,
    Course,
    CourseProgress,
    Enrollment,
    Favorite,
    GrowthEvent,
    GrowthPlan,
    GrowthTask,
    Mentor,
    MentorConsultation,
    Opportunity,
    Policy,
    ProactiveSuggestion,
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


@admin.register(AgentBindingCode)
class AgentBindingCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used_at", "created_at")
    list_filter = ("used_at",)
    search_fields = ("user__username",)


@admin.register(AgentUserBinding)
class AgentUserBindingAdmin(admin.ModelAdmin):
    list_display = ("platform", "external_user_id", "user", "is_active", "bound_at")
    list_filter = ("platform", "is_active")
    search_fields = ("external_user_id", "user__username")


@admin.register(AgentConversation)
class AgentConversationAdmin(admin.ModelAdmin):
    list_display = ("platform", "external_conversation_id", "user", "last_interacted_at")
    list_filter = ("platform",)
    search_fields = ("external_conversation_id", "user__username", "summary")


@admin.register(AgentMessage)
class AgentMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("content_summary",)


@admin.register(GrowthPlan)
class GrowthPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "goal", "status", "starts_on", "ends_on", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "goal")


@admin.register(GrowthTask)
class GrowthTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "plan", "stage", "status", "due_at")
    list_filter = ("stage", "status", "action_type")
    search_fields = ("title", "plan__user__username")


@admin.register(AgentToolLog)
class AgentToolLogAdmin(admin.ModelAdmin):
    list_display = ("skill_name", "user", "result_status", "duration_ms", "created_at")
    list_filter = ("skill_name", "result_status")
    search_fields = ("skill_name", "user__username")


@admin.register(ProactiveSuggestion)
class ProactiveSuggestionAdmin(admin.ModelAdmin):
    list_display = ("user", "suggestion_type", "scheduled_for", "viewed_at", "completed_at")
    list_filter = ("suggestion_type", "viewed_at", "completed_at")
    search_fields = ("user__username", "content", "trigger_reason")
