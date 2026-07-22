import json
import secrets
from functools import wraps
from time import perf_counter

from django.conf import settings

from .agent_protocol import agent_response
from .models import AgentToolLog, AgentUserBinding


def _request_summary(data):
    summary = {"fields": sorted(data.keys())}
    for field in ("action", "resourceId", "resourceType", "operation"):
        if field in data:
            summary[field] = data[field]
    return summary


def service_key_is_valid(request):
    configured_key = settings.AGENT_SERVICE_KEY
    provided_key = request.headers.get("X-Agent-Service-Key", "")
    return bool(configured_key and provided_key) and secrets.compare_digest(
        configured_key, provided_key
    )


def agent_service_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not service_key_is_valid(request):
            return agent_response(
                ok=False,
                message="Agent 服务凭据无效",
                error_code="INVALID_SERVICE_CREDENTIAL",
                status=401,
            )
        return view_func(request, *args, **kwargs)

    return wrapper


def agent_skill(skill_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not service_key_is_valid(request):
                return agent_response(
                    ok=False,
                    message="Agent 服务凭据无效",
                    error_code="INVALID_SERVICE_CREDENTIAL",
                    status=401,
                )

            started_at = perf_counter()
            user = None
            result_status = AgentToolLog.RESULT_ERROR
            try:
                try:
                    data = json.loads(request.body.decode("utf-8")) if request.body else {}
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return agent_response(
                        ok=False,
                        message="请求内容不是有效 JSON",
                        error_code="INVALID_JSON",
                        status=400,
                    )
                if not isinstance(data, dict):
                    return agent_response(
                        ok=False,
                        message="请求内容必须是对象",
                        error_code="INVALID_JSON",
                        status=400,
                    )

                request.agent_data = data
                external_user_id = str(data.get("externalUserId") or "").strip()
                binding = AgentUserBinding.objects.select_related("user").filter(
                    platform="xiaoyi",
                    external_user_id=external_user_id,
                    is_active=True,
                ).first()
                if not binding:
                    return agent_response(
                        ok=False,
                        message="请先在冀青赋能小程序绑定账号",
                        error_code="AGENT_USER_NOT_BOUND",
                        status=403,
                    )

                user = binding.user
                request.agent_user = user
                response = view_func(request, *args, **kwargs)
                result_status = AgentToolLog.RESULT_SUCCESS if response.status_code < 400 else AgentToolLog.RESULT_ERROR
                return response
            finally:
                data = getattr(request, "agent_data", {})
                AgentToolLog.objects.create(
                    user=user,
                    skill_name=skill_name,
                    request_summary=_request_summary(data),
                    result_status=result_status,
                    duration_ms=max(0, int((perf_counter() - started_at) * 1000)),
                )

        return wrapper

    return decorator
