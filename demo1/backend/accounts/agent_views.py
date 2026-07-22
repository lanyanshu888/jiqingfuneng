from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .agent_auth import agent_skill
from .agent_protocol import agent_response


@csrf_exempt
@require_http_methods(["POST"])
@agent_skill("profile_context")
def profile_context(request):
    return agent_response(
        ok=True,
        message="画像已读取",
        data={"profile": {}, "missingFields": [], "recentGrowth": []},
    )
