import json
from datetime import date
from functools import wraps

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import AuthToken, YouthProfile
from django.utils import timezone

from .models import Activity, Course, CourseProgress, Enrollment, GrowthEvent, Mentor, Opportunity, Policy


def json_body(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.first_name or user.username,
    }


def profile_payload(profile):
    return {
        "nickname": profile.nickname,
        "age": profile.age,
        "region": profile.region,
        "education": profile.education,
        "major": profile.major,
        "status": profile.status,
        "type": profile.profile_type,
        "intents": profile.intents,
        "abilities": profile.abilities,
        "tags": profile.tags,
        "summary": profile.summary,
    }


def policy_payload(policy):
    return {
        "id": policy.id,
        "title": policy.title,
        "region": policy.region,
        "category": policy.category,
        "target": policy.target,
        "support": policy.support,
        "conditions": policy.conditions,
        "materials": policy.materials,
        "process": policy.process,
        "location": policy.location,
        "phone": policy.phone,
        "source": policy.source,
        "publishedAt": policy.published_at.isoformat() if policy.published_at else None,
        "effectiveUntil": policy.effective_until.isoformat() if policy.effective_until else None,
    }


def resource_payload(resource):
    payload = {"id": resource.id, "title": resource.title}
    for field in ("region", "category", "type", "unit", "pay", "education", "major", "tags", "detail", "target", "duration", "teacher", "goal", "materials", "certificate", "place", "host", "capacity", "agenda", "role", "good_at", "available"):
        if hasattr(resource, field):
            payload[field] = getattr(resource, field)
    if hasattr(resource, "deadline"):
        payload["deadline"] = resource.deadline.isoformat() if resource.deadline else None
    if hasattr(resource, "starts_at"):
        payload["startsAt"] = resource.starts_at.isoformat() if resource.starts_at else None
    return payload


def published_items(model):
    return model.objects.filter(status=model.STATUS_PUBLISHED).order_by("-created_at")


def published_resource_detail(model, resource_id, message):
    resource = model.objects.filter(id=resource_id, status=model.STATUS_PUBLISHED).first()
    if not resource:
        return JsonResponse({"message": message}, status=404)
    return JsonResponse(resource_payload(resource))


def auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        header = request.headers.get("Authorization", "")
        prefix = "Token "
        if not header.startswith(prefix):
            return JsonResponse({"message": "请先登录"}, status=401)
        token_key = header[len(prefix):].strip()
        token = AuthToken.objects.select_related("user").filter(key=token_key).first()
        if not token:
            return JsonResponse({"message": "登录已失效，请重新登录"}, status=401)
        request.user = token.user
        return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    data = json_body(request)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or username).strip()

    if not username or not password:
        return JsonResponse({"message": "账号和密码不能为空"}, status=400)
    if len(password) < 6:
        return JsonResponse({"message": "密码不少于6位"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"message": "账号已存在"}, status=400)

    user = User.objects.create_user(username=username, password=password, first_name=nickname)
    YouthProfile.objects.create(user=user, nickname=nickname)
    token = AuthToken.create_for_user(user)
    return JsonResponse({"token": token.key, "user": user_payload(user)})


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    data = json_body(request)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"message": "账号或密码错误"}, status=400)

    AuthToken.objects.filter(user=user).delete()
    token = AuthToken.create_for_user(user)
    return JsonResponse({"token": token.key, "user": user_payload(user)})


@csrf_exempt
@require_http_methods(["GET"])
@auth_required
def me(request):
    profile = YouthProfile.objects.filter(user=request.user).first()
    return JsonResponse({
        "user": user_payload(request.user),
        "profile": profile_payload(profile) if profile else None,
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
@auth_required
def profile_me(request):
    profile, _created = YouthProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse({"profile": profile_payload(profile)})

    data = json_body(request)
    profile.nickname = data.get("nickname") or profile.nickname
    profile.age = int(data["age"]) if str(data.get("age") or "").isdigit() else profile.age
    profile.region = data.get("region") or ""
    profile.education = data.get("education") or ""
    profile.major = data.get("major") or ""
    profile.status = data.get("status") or ""
    profile.profile_type = data.get("type") or ""
    profile.intents = data.get("intents") or []
    profile.abilities = data.get("abilities") or []
    profile.tags = data.get("tags") or []
    profile.summary = data.get("summary") or ""
    profile.save()

    return JsonResponse({"profile": profile_payload(profile)})


@require_http_methods(["GET"])
def policy_list(request):
    policies = Policy.objects.filter(status=Policy.STATUS_PUBLISHED).filter(
        models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=date.today())
    ).order_by("-created_at")
    return JsonResponse({"items": [policy_payload(policy) for policy in policies]})


@require_http_methods(["GET"])
def policy_detail(request, policy_id):
    policy = Policy.objects.filter(id=policy_id, status=Policy.STATUS_PUBLISHED).filter(
        models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=date.today())
    ).first()
    if not policy:
        return JsonResponse({"message": "政策不存在"}, status=404)
    return JsonResponse(policy_payload(policy))


@require_http_methods(["GET"])
def opportunity_list(request):
    return JsonResponse({"items": [resource_payload(item) for item in published_items(Opportunity).filter(models.Q(deadline__isnull=True) | models.Q(deadline__gte=date.today()))]})


@require_http_methods(["GET"])
def opportunity_detail(request, opportunity_id):
    return published_resource_detail(Opportunity, opportunity_id, "岗位不存在")


@require_http_methods(["GET"])
def course_list(request):
    return JsonResponse({"items": [resource_payload(item) for item in published_items(Course)]})


@require_http_methods(["GET"])
def course_detail(request, course_id):
    return published_resource_detail(Course, course_id, "课程不存在")


@require_http_methods(["GET"])
def activity_list(request):
    return JsonResponse({"items": [resource_payload(item) for item in published_items(Activity)]})


@require_http_methods(["GET"])
def activity_detail(request, activity_id):
    return published_resource_detail(Activity, activity_id, "活动不存在")


@require_http_methods(["GET"])
def mentor_list(request):
    return JsonResponse({"items": [resource_payload(item) for item in published_items(Mentor)]})


@csrf_exempt
@require_http_methods(["POST"])
@auth_required
def enroll_activity(request, activity_id):
    activity = Activity.objects.filter(id=activity_id, status=Activity.STATUS_PUBLISHED).first()
    if not activity:
        return JsonResponse({"message": "活动不存在"}, status=404)
    if Enrollment.objects.filter(user=request.user, activity=activity).exists():
        return JsonResponse({"message": "你已报名该活动"}, status=409)
    Enrollment.objects.create(user=request.user, activity=activity)
    GrowthEvent.objects.create(
        user=request.user,
        event_type="activity_enrolled",
        resource_type="activity",
        resource_id=activity.id,
    )
    return JsonResponse({"message": "报名成功", "activityId": activity.id}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
@auth_required
def enroll_opportunity(request, opportunity_id):
    opportunity = Opportunity.objects.filter(id=opportunity_id, status=Opportunity.STATUS_PUBLISHED).first()
    if not opportunity:
        return JsonResponse({"message": "岗位不存在"}, status=404)
    if Enrollment.objects.filter(user=request.user, opportunity=opportunity).exists():
        return JsonResponse({"message": "你已申请该岗位"}, status=409)
    Enrollment.objects.create(user=request.user, opportunity=opportunity)
    GrowthEvent.objects.create(
        user=request.user,
        event_type="opportunity_enrolled",
        resource_type="opportunity",
        resource_id=opportunity.id,
    )
    return JsonResponse({"message": "申请成功", "opportunityId": opportunity.id}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
@auth_required
def complete_course(request, course_id):
    course = Course.objects.filter(id=course_id, status=Course.STATUS_PUBLISHED).first()
    if not course:
        return JsonResponse({"message": "课程不存在"}, status=404)
    progress, created = CourseProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={"completed": True, "completed_at": timezone.now()},
    )
    if not created and progress.completed:
        return JsonResponse({"message": "你已完成该课程"}, status=409)
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save(update_fields=["completed", "completed_at"])
    GrowthEvent.objects.create(
        user=request.user,
        event_type="course_completed",
        resource_type="course",
        resource_id=course.id,
    )
    return JsonResponse({"message": "课程已完成", "courseId": course.id}, status=201)


@require_http_methods(["GET"])
@auth_required
def growth_records(request):
    activity_enrollments = Enrollment.objects.filter(user=request.user, activity__isnull=False).select_related("activity").order_by("-created_at")
    opportunity_enrollments = Enrollment.objects.filter(user=request.user, opportunity__isnull=False).select_related("opportunity").order_by("-created_at")
    completed_courses = CourseProgress.objects.filter(user=request.user, completed=True).select_related("course").order_by("-completed_at")
    return JsonResponse({
        "activities": [resource_payload(item.activity) for item in activity_enrollments],
        "opportunities": [resource_payload(item.opportunity) for item in opportunity_enrollments],
        "courses": [resource_payload(item.course) for item in completed_courses],
    })
