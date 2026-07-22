from django.http import JsonResponse


def agent_response(
    *,
    ok,
    message,
    data=None,
    sources=None,
    requires_confirmation=False,
    error_code=None,
    status=200,
):
    return JsonResponse(
        {
            "ok": ok,
            "message": message,
            "data": data or {},
            "sources": sources or [],
            "requiresConfirmation": requires_confirmation,
            "errorCode": error_code,
        },
        status=status,
    )
