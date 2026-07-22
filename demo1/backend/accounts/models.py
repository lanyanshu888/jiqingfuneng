import secrets

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
