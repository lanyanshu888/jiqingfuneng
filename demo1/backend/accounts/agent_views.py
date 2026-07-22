import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .agent_auth import agent_service_required, agent_skill
from .agent_actions import AgentActionError, execute_action, prepare_action
from .agent_protocol import agent_response
from .agent_services import (
    REQUIRED_PROFILE_FIELDS,
    create_career_plan,
    match_resources,
    profile_context_data,
    search_policies,
    update_profile_from_agent,
)
from .models import AgentBindingCode, AgentUserBinding
from .views import auth_required, json_body


BINDING_CODE_LIFETIME_SECONDS = 600


def _code_digest(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


@csrf_exempt
@require_http_methods(["POST"])
@auth_required
def create_binding_code(request):
    now = timezone.now()
    AgentBindingCode.objects.filter(
        user=request.user,
        used_at__isnull=True,
        expires_at__gt=now,
    ).update(expires_at=now)

    for _attempt in range(20):
        code = str(secrets.randbelow(900000) + 100000)
        digest = _code_digest(code)
        if not AgentBindingCode.objects.filter(code_digest=digest).exists():
            break
    else:
        return JsonResponse({"message": "绑定码生成失败，请稍后重试"}, status=503)

    expires_at = now + timedelta(seconds=BINDING_CODE_LIFETIME_SECONDS)
    AgentBindingCode.objects.create(
        user=request.user,
        code_digest=digest,
        expires_at=expires_at,
    )
    return JsonResponse(
        {
            "code": code,
            "expiresAt": expires_at.isoformat(),
            "expiresIn": BINDING_CODE_LIFETIME_SECONDS,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
@agent_service_required
def bind_account(request):
    data = json_body(request)
    external_user_id = str(data.get("externalUserId") or "").strip()
    code = str(data.get("code") or "").strip()
    if not external_user_id:
        return agent_response(
            ok=False,
            message="缺少小艺用户标识",
            error_code="EXTERNAL_ID_REQUIRED",
            status=400,
        )
    if not code:
        return agent_response(
            ok=False,
            message="绑定码无效或已使用",
            error_code="BINDING_CODE_INVALID",
            status=400,
        )

    with transaction.atomic():
        binding_code = AgentBindingCode.objects.select_for_update().filter(
            code_digest=_code_digest(code)
        ).first()
        if not binding_code or binding_code.used_at:
            return agent_response(
                ok=False,
                message="绑定码无效或已使用",
                error_code="BINDING_CODE_INVALID",
                status=400,
            )
        if binding_code.expires_at <= timezone.now():
            return agent_response(
                ok=False,
                message="绑定码已过期，请在小程序重新生成",
                error_code="BINDING_CODE_EXPIRED",
                status=400,
            )

        external_binding = AgentUserBinding.objects.select_for_update().filter(
            platform="xiaoyi", external_user_id=external_user_id
        ).first()
        if external_binding and external_binding.user_id != binding_code.user_id:
            return agent_response(
                ok=False,
                message="该小艺账号已绑定其他用户",
                error_code="EXTERNAL_ID_ALREADY_BOUND",
                status=409,
            )

        AgentUserBinding.objects.filter(
            platform="xiaoyi", user=binding_code.user, is_active=True
        ).exclude(external_user_id=external_user_id).update(is_active=False)
        AgentUserBinding.objects.update_or_create(
            platform="xiaoyi",
            external_user_id=external_user_id,
            defaults={"user": binding_code.user, "is_active": True},
        )
        binding_code.used_at = timezone.now()
        binding_code.save(update_fields=["used_at"])

    return agent_response(
        ok=True,
        message="账号绑定成功",
        data={"bound": True, "platform": "xiaoyi"},
    )


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("profile_context")
def profile_context(request):
    data = request.agent_data
    if data.get("operation") == "update":
        changes = data.get("changes") if isinstance(data.get("changes"), dict) else {}
        if not data.get("confirmed"):
            return agent_response(
                ok=True,
                message="请确认是否更新青年画像",
                data={"changes": changes},
                requires_confirmation=True,
            )
        context = update_profile_from_agent(request.agent_user, changes)
        return agent_response(ok=True, message="青年画像已更新", data=context)

    return agent_response(
        ok=True,
        message="画像已读取",
        data=profile_context_data(request.agent_user),
    )


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("policy_search")
def policy_search(request):
    data = request.agent_data
    result, sources = search_policies(
        request.agent_user,
        keyword=data.get("keyword"),
        region=data.get("region"),
        category=data.get("category"),
        limit=data.get("limit", 5),
    )
    message = f"找到 {len(result['items'])} 条可能适用的政策" if result["items"] else "暂未找到符合条件的政策"
    return agent_response(ok=True, message=message, data=result, sources=sources)


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("resource_match")
def resource_match(request):
    data = request.agent_data
    result = match_resources(
        request.agent_user,
        resource_types=data.get("resourceTypes"),
        goal=data.get("goal"),
        limit=data.get("limit", 3),
    )
    return agent_response(
        ok=True,
        message=f"为你匹配到 {len(result['items'])} 项成长资源",
        data=result,
    )


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("career_plan")
def career_plan(request):
    data = request.agent_data
    goal = str(data.get("goal") or "").strip()[:255]
    context = profile_context_data(request.agent_user)
    missing_fields = list(context["missingFields"])
    if not goal:
        missing_fields.insert(0, "goal")
    missing_fields = [field for field in ["goal", *REQUIRED_PROFILE_FIELDS] if field in missing_fields]
    if missing_fields:
        return agent_response(
            ok=False,
            message="请先补充制定规划所需的信息",
            data={"missingFields": missing_fields},
            error_code="PROFILE_INCOMPLETE",
            status=400,
        )
    result = create_career_plan(request.agent_user, goal)
    return agent_response(
        ok=True,
        message="已生成 7 天、1 个月和 3 个月成长计划",
        data=result,
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("growth_action")
def growth_action(request):
    data = request.agent_data
    action = data.get("action")
    resource_id = data.get("resourceId")
    resource_type = data.get("resourceType", "")
    try:
        if not data.get("confirmed"):
            preview = prepare_action(
                request.agent_user, action, resource_id, resource_type
            )
            return agent_response(
                ok=True,
                message=f"请确认是否执行：{preview['title']}",
                data=preview,
                requires_confirmation=True,
            )
        result, created = execute_action(
            request.agent_user,
            action,
            resource_id,
            resource_type,
            str(data.get("confirmationToken") or ""),
        )
    except AgentActionError as exc:
        return agent_response(
            ok=False,
            message=exc.message,
            error_code=exc.code,
            status=exc.status,
        )
    return agent_response(
        ok=True,
        message="操作已完成" if created else "该操作此前已完成",
        data=result,
        status=201 if created else 200,
    )
