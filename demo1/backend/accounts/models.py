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
