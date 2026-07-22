import secrets
import hashlib
from datetime import date

from django.conf import settings
from django.db import models


class AuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_tokens")
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_for_user(cls, user):
        return cls.objects.create(user=user, key=secrets.token_hex(32))

    def __str__(self):
        return f"{self.user_id}:{self.key[:8]}"


class YouthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="youth_profile")
    nickname = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=50, blank=True)
    major = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, blank=True)
    profile_type = models.CharField(max_length=50, blank=True)
    intents = models.JSONField(default=list, blank=True)
    abilities = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    summary = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or self.user.username


class PublishedResource(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_PENDING, "待审核"),
        (STATUS_PUBLISHED, "已发布"),
    ]

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Policy(PublishedResource):
    region = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    target = models.TextField(blank=True)
    support = models.TextField(blank=True)
    conditions = models.JSONField(default=list, blank=True)
    materials = models.JSONField(default=list, blank=True)
    process = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=255, blank=True)
    published_at = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)


class Opportunity(PublishedResource):
    type = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=200, blank=True)
    region = models.CharField(max_length=100, blank=True)
    pay = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    major = models.CharField(max_length=200, blank=True)
    deadline = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    detail = models.TextField(blank=True)


class Course(PublishedResource):
    category = models.CharField(max_length=50, blank=True)
    target = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=50, blank=True)
    teacher = models.CharField(max_length=100, blank=True)
    goal = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    certificate = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)


class Activity(PublishedResource):
    starts_at = models.DateTimeField(null=True, blank=True)
    place = models.CharField(max_length=200, blank=True)
    host = models.CharField(max_length=200, blank=True)
    target = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    agenda = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)


class Mentor(PublishedResource):
    role = models.CharField(max_length=100, blank=True)
    good_at = models.TextField(blank=True)
    available = models.CharField(max_length=100, blank=True)


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.CASCADE, related_name="enrollments")
    opportunity = models.ForeignKey(Opportunity, null=True, blank=True, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "activity"], name="unique_activity_enrollment"),
            models.UniqueConstraint(fields=["user", "opportunity"], name="unique_opportunity_enrollment"),
        ]


class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_progresses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progresses")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="unique_course_progress")]


class MentorConsultation(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CHOICES = [(STATUS_PENDING, "待处理"), ("replied", "已回复"), ("closed", "已结束")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultations")
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="consultations")
    scheduled_at = models.CharField(max_length=100, blank=True)
    question = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    resource_type = models.CharField(max_length=30)
    resource_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "resource_type", "resource_id"], name="unique_favorite")]


class GrowthEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="growth_events")
    event_type = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=30, blank=True)
    resource_id = models.PositiveIntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ReviewItem(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    resource_type = models.CharField(max_length=30)
    resource_id = models.PositiveIntegerField()
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="submitted_reviews")
    status = models.CharField(max_length=20, default=STATUS_PENDING)
    comment = models.TextField(blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_items")
    reviewed_at = models.DateTimeField(null=True, blank=True)


class AgentBindingCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_binding_codes")
    code_digest = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "expires_at"], name="agent_code_user_exp_idx")]


class AgentUserBinding(models.Model):
    platform = models.CharField(max_length=30, default="xiaoyi")
    external_user_id = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_bindings")
    access_token_digest = models.CharField(max_length=64, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    bound_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["platform", "external_user_id"], name="unique_agent_external_id"),
            models.UniqueConstraint(
                fields=["platform", "user"],
                condition=models.Q(is_active=True),
                name="unique_active_agent_user",
            ),
        ]
        indexes = [models.Index(fields=["platform", "external_user_id", "is_active"], name="agent_binding_lookup_idx")]

    @staticmethod
    def digest_access_token(token):
        return hashlib.sha256(str(token).encode("utf-8")).hexdigest()

    def issue_access_token(self):
        token = secrets.token_urlsafe(32)
        self.access_token_digest = self.digest_access_token(token)
        self.save(update_fields=["access_token_digest"])
        return token


class AgentConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_conversations")
    platform = models.CharField(max_length=30, default="xiaoyi")
    external_conversation_id = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    last_interacted_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "external_conversation_id"],
                name="unique_agent_conversation",
            )
        ]


class AgentMessage(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_TOOL = "tool"
    ROLE_CHOICES = [
        (ROLE_USER, "用户"),
        (ROLE_ASSISTANT, "Agent"),
        (ROLE_TOOL, "工具"),
    ]

    conversation = models.ForeignKey(AgentConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GrowthPlan(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_REPLACED = "replaced"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "进行中"),
        (STATUS_COMPLETED, "已完成"),
        (STATUS_REPLACED, "已更新"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="growth_plans")
    goal = models.CharField(max_length=255)
    starts_on = models.DateField(default=date.today)
    ends_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    rationale = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "status", "-created_at"], name="growth_plan_user_idx")]


class GrowthTask(models.Model):
    STAGE_SEVEN_DAYS = "seven_days"
    STAGE_ONE_MONTH = "one_month"
    STAGE_THREE_MONTHS = "three_months"
    STAGE_CHOICES = [
        (STAGE_SEVEN_DAYS, "7天"),
        (STAGE_ONE_MONTH, "1个月"),
        (STAGE_THREE_MONTHS, "3个月"),
    ]
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_SKIPPED = "skipped"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待完成"),
        (STATUS_COMPLETED, "已完成"),
        (STATUS_SKIPPED, "已跳过"),
    ]

    plan = models.ForeignKey(GrowthPlan, on_delete=models.CASCADE, related_name="tasks")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    title = models.CharField(max_length=200)
    action_type = models.CharField(max_length=50, blank=True)
    resource_type = models.CharField(max_length=30, blank=True)
    resource_id = models.PositiveIntegerField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sequence", "id"]
        indexes = [models.Index(fields=["plan", "stage", "status"], name="growth_task_plan_idx")]


class AgentToolLog(models.Model):
    RESULT_SUCCESS = "success"
    RESULT_ERROR = "error"
    RESULT_CHOICES = [(RESULT_SUCCESS, "成功"), (RESULT_ERROR, "失败")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="agent_tool_logs")
    skill_name = models.CharField(max_length=80)
    request_summary = models.JSONField(default=dict, blank=True)
    result_status = models.CharField(max_length=20, choices=RESULT_CHOICES)
    duration_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["skill_name", "-created_at"], name="agent_tool_skill_idx")]


class ProactiveSuggestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proactive_suggestions")
    suggestion_type = models.CharField(max_length=50)
    content = models.TextField()
    trigger_reason = models.CharField(max_length=255)
    scheduled_for = models.DateTimeField()
    viewed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "scheduled_for", "completed_at"], name="agent_suggestion_user_idx")]
