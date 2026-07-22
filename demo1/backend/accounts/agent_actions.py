from datetime import date

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils import timezone

from .models import (
    Activity,
    Course,
    CourseProgress,
    Enrollment,
    Favorite,
    GrowthEvent,
    GrowthTask,
    Opportunity,
    Policy,
)


SIGNING_SALT = "jiqing-agent-action"
ACTION_RESOURCE_TYPES = {
    "enroll_activity": "activity",
    "apply_opportunity": "opportunity",
    "complete_course": "course",
    "complete_task": "task",
}
FAVORITE_MODELS = {
    "policy": Policy,
    "opportunity": Opportunity,
    "course": Course,
    "activity": Activity,
}


class AgentActionError(Exception):
    def __init__(self, message, code, status=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


def _normalize(user, action, resource_id, resource_type=""):
    action = str(action or "").strip()
    if action not in {*ACTION_RESOURCE_TYPES, "favorite_resource"}:
        raise AgentActionError("不支持该操作", "ACTION_NOT_SUPPORTED")
    if not str(resource_id or "").isdigit() or int(resource_id) <= 0:
        raise AgentActionError("资源编号无效", "RESOURCE_ID_INVALID")
    resolved_type = ACTION_RESOURCE_TYPES.get(action, str(resource_type or "").strip())
    if action == "favorite_resource" and resolved_type not in FAVORITE_MODELS:
        raise AgentActionError("收藏资源类型无效", "RESOURCE_TYPE_INVALID")
    payload = {
        "userId": user.id,
        "action": action,
        "resourceType": resolved_type,
        "resourceId": int(resource_id),
    }
    return payload


def _resource_for_action(user, payload):
    action = payload["action"]
    resource_id = payload["resourceId"]
    if action == "enroll_activity":
        resource = Activity.objects.filter(id=resource_id, status="published").first()
        if resource and resource.starts_at and resource.starts_at < timezone.now():
            resource = None
    elif action == "apply_opportunity":
        resource = Opportunity.objects.filter(id=resource_id, status="published").first()
        if resource and resource.deadline and resource.deadline < date.today():
            resource = None
    elif action == "complete_course":
        resource = Course.objects.filter(id=resource_id, status="published").first()
    elif action == "complete_task":
        resource = GrowthTask.objects.filter(id=resource_id, plan__user=user).first()
    else:
        model = FAVORITE_MODELS[payload["resourceType"]]
        resource = model.objects.filter(id=resource_id, status="published").first()
    if not resource:
        raise AgentActionError("资源不存在、已过期或不可操作", "RESOURCE_UNAVAILABLE", 404)
    return resource


def prepare_action(user, action, resource_id, resource_type=""):
    payload = _normalize(user, action, resource_id, resource_type)
    resource = _resource_for_action(user, payload)
    token = signing.dumps(payload, salt=SIGNING_SALT, compress=True)
    return {
        "confirmationToken": token,
        "action": payload["action"],
        "resourceType": payload["resourceType"],
        "resourceId": payload["resourceId"],
        "title": resource.title,
    }


def _confirmed_payload(user, action, resource_id, resource_type, token):
    expected = _normalize(user, action, resource_id, resource_type)
    try:
        actual = signing.loads(
            token,
            salt=SIGNING_SALT,
            max_age=settings.AGENT_CONFIRMATION_MAX_AGE_SECONDS,
        )
    except signing.SignatureExpired as exc:
        raise AgentActionError("确认已过期，请重新确认", "CONFIRMATION_EXPIRED") from exc
    except signing.BadSignature as exc:
        raise AgentActionError("确认标识无效", "CONFIRMATION_INVALID") from exc
    if actual != expected:
        raise AgentActionError("确认内容与当前操作不一致", "CONFIRMATION_MISMATCH")
    return actual


@transaction.atomic
def execute_action(user, action, resource_id, resource_type, token):
    payload = _confirmed_payload(user, action, resource_id, resource_type, token)
    resource = _resource_for_action(user, payload)
    action = payload["action"]
    if action == "enroll_activity":
        _record, created = Enrollment.objects.get_or_create(user=user, activity=resource)
        event_type = "activity_enrolled"
    elif action == "apply_opportunity":
        _record, created = Enrollment.objects.get_or_create(user=user, opportunity=resource)
        event_type = "opportunity_enrolled"
    elif action == "complete_course":
        progress, created = CourseProgress.objects.get_or_create(
            user=user,
            course=resource,
            defaults={"completed": True, "completed_at": timezone.now()},
        )
        if not created and not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save(update_fields=["completed", "completed_at"])
            created = True
        event_type = "course_completed"
    elif action == "complete_task":
        created = resource.status != GrowthTask.STATUS_COMPLETED
        if created:
            resource.status = GrowthTask.STATUS_COMPLETED
            resource.completed_at = timezone.now()
            resource.save(update_fields=["status", "completed_at"])
        event_type = "growth_task_completed"
    else:
        _record, created = Favorite.objects.get_or_create(
            user=user,
            resource_type=payload["resourceType"],
            resource_id=resource.id,
        )
        event_type = "resource_favorited"

    if created:
        GrowthEvent.objects.create(
            user=user,
            event_type=event_type,
            resource_type=payload["resourceType"],
            resource_id=resource.id,
        )
    return {
        "executed": True,
        "alreadyCompleted": not created,
        "action": action,
        "resourceType": payload["resourceType"],
        "resourceId": resource.id,
        "title": resource.title,
    }, created
