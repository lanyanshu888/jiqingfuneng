import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .agent_auth import agent_service_required, agent_skill
from .agent_protocol import agent_response
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
    return agent_response(
        ok=True,
        message="画像已读取",
        data={"profile": {}, "missingFields": [], "recentGrowth": []},
    )
