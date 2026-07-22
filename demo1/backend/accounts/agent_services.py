from datetime import date, timedelta

from django.db import models, transaction
from django.utils import timezone

from .models import Activity, Course, GrowthPlan, GrowthTask, Mentor, Opportunity, Policy
from .models import GrowthEvent, YouthProfile


PROFILE_FIELDS = (
    "nickname",
    "age",
    "region",
    "education",
    "major",
    "status",
    "profile_type",
    "intents",
    "abilities",
    "tags",
    "summary",
)
REQUIRED_PROFILE_FIELDS = ("region", "education", "major", "intents", "abilities")


def profile_context_data(user):
    profile, _created = YouthProfile.objects.get_or_create(user=user)
    payload = {field: getattr(profile, field) for field in PROFILE_FIELDS}
    payload["type"] = payload.pop("profile_type")
    missing_fields = [
        field for field in REQUIRED_PROFILE_FIELDS if not getattr(profile, field)
    ]
    recent_growth = [
        {
            "eventType": event.event_type,
            "resourceType": event.resource_type,
            "resourceId": event.resource_id,
            "createdAt": event.created_at.isoformat(),
        }
        for event in GrowthEvent.objects.filter(user=user).order_by("-created_at")[:10]
    ]
    return {
        "profile": payload,
        "missingFields": missing_fields,
        "recentGrowth": recent_growth,
    }


def update_profile_from_agent(user, changes):
    profile, _created = YouthProfile.objects.get_or_create(user=user)
    allowed_fields = set(PROFILE_FIELDS) - {"profile_type"}
    allowed_fields.add("type")
    changed_fields = []
    for field, value in changes.items():
        if field not in allowed_fields:
            continue
        model_field = "profile_type" if field == "type" else field
        if model_field in {"intents", "abilities", "tags"}:
            value = value if isinstance(value, list) else []
        elif model_field == "age":
            value = int(value) if str(value or "").isdigit() else None
        else:
            value = str(value or "").strip()
        setattr(profile, model_field, value)
        changed_fields.append(model_field)
    if changed_fields:
        profile.save()
        GrowthEvent.objects.create(
            user=user,
            event_type="profile_updated_by_agent",
            payload={"fields": sorted(changed_fields)},
        )
    return profile_context_data(user)


def _text_contains(value, query):
    return not query or query.lower() in str(value or "").lower()


def _regions_match(resource_region, requested_region):
    if not requested_region or not resource_region:
        return True
    normalized_resource = resource_region.replace("河北省", "").replace("河北", "")
    normalized_requested = requested_region.replace("河北省", "").replace("河北", "")
    return (
        normalized_resource in normalized_requested
        or normalized_requested in normalized_resource
    )


def search_policies(user, keyword="", region="", category="", limit=5):
    profile = YouthProfile.objects.filter(user=user).first()
    requested_region = str(region or (profile.region if profile else ""))[:100].strip()
    keyword = str(keyword or "")[:50].strip()
    category = str(category or "")[:50].strip()
    policies = Policy.objects.filter(status=Policy.STATUS_PUBLISHED).filter(
        models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=date.today())
    ).order_by("-published_at", "-created_at")

    matched = []
    for policy in policies:
        if category and policy.category != category:
            continue
        if not _regions_match(policy.region, requested_region):
            continue
        searchable = " ".join([
            policy.title,
            policy.target,
            policy.support,
            str(policy.conditions),
            str(policy.materials),
        ])
        if not _text_contains(searchable, keyword):
            continue
        matched.append(policy)
        if len(matched) >= max(1, min(int(limit or 5), 5)):
            break

    items = []
    sources = []
    for policy in matched:
        reasons = []
        if requested_region and _regions_match(policy.region, requested_region):
            reasons.append("政策地区与你的所在地匹配")
        if keyword:
            reasons.append(f"政策内容包含“{keyword}”相关信息")
        items.append({
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
            "applicabilityReasons": reasons,
            "uncertainConditions": policy.conditions,
        })
        sources.append({
            "title": policy.title,
            "publisher": policy.source,
            "publishedAt": policy.published_at.isoformat() if policy.published_at else None,
            "effectiveUntil": policy.effective_until.isoformat() if policy.effective_until else None,
        })
    return {"items": items, "query": {"keyword": keyword, "region": requested_region}}, sources


RESOURCE_MODELS = {
    "opportunity": Opportunity,
    "course": Course,
    "activity": Activity,
    "mentor": Mentor,
}


def _active_resources(resource_type, model):
    queryset = model.objects.filter(status=model.STATUS_PUBLISHED)
    if resource_type == "opportunity":
        queryset = queryset.filter(
            models.Q(deadline__isnull=True) | models.Q(deadline__gte=date.today())
        )
    if resource_type == "activity":
        queryset = queryset.filter(
            models.Q(starts_at__isnull=True) | models.Q(starts_at__gte=timezone.now())
        )
    return queryset


def _resource_score(resource_type, resource, profile, goal):
    score = 10
    reasons = ["资源当前有效且已发布"]
    resource_text = " ".join(
        str(getattr(resource, field, "") or "")
        for field in (
            "title", "region", "tags", "major", "education", "detail",
            "target", "goal", "role", "good_at",
        )
    )
    if profile and profile.region and getattr(resource, "region", ""):
        if _regions_match(getattr(resource, "region"), profile.region):
            score += 30
            reasons.append("所在地区匹配")

    intents = profile.intents if profile else []
    intent_match = (
        resource_type == "opportunity" and any("工作" in item or "实习" in item for item in intents)
    ) or (
        resource_type == "course" and any("技能" in item or "学习" in item for item in intents)
    ) or (
        resource_type == "activity" and any("实践" in item or "活动" in item for item in intents)
    ) or (
        resource_type == "mentor" and any("创业" in item or "导师" in item for item in intents)
    )
    if intent_match:
        score += 25
        reasons.append("符合你的发展意向")

    profile_tags = set(profile.tags if profile else [])
    resource_tags = set(getattr(resource, "tags", []) or [])
    shared_tags = sorted(profile_tags & resource_tags)
    if shared_tags:
        score += min(20, len(shared_tags) * 10)
        reasons.append("共同标签：" + "、".join(shared_tags))

    qualification_matches = []
    if profile and profile.major and profile.major in resource_text:
        qualification_matches.append("专业")
    if profile and profile.education and profile.education in resource_text:
        qualification_matches.append("学历")
    if qualification_matches:
        score += 15
        reasons.append("、".join(qualification_matches) + "条件匹配")
    if goal and goal in resource_text:
        score += 10
        reasons.append("与当前目标关键词匹配")
    return min(score, 100), reasons


def match_resources(user, resource_types=None, goal="", limit=3):
    profile = YouthProfile.objects.filter(user=user).first()
    selected_types = resource_types if isinstance(resource_types, list) else list(RESOURCE_MODELS)
    selected_types = [item for item in selected_types if item in RESOURCE_MODELS]
    per_type_limit = max(1, min(int(limit or 3), 5))
    items = []
    for resource_type in selected_types:
        ranked = []
        for resource in _active_resources(resource_type, RESOURCE_MODELS[resource_type]):
            score, reasons = _resource_score(resource_type, resource, profile, str(goal or "")[:100])
            ranked.append((score, resource.id, resource, reasons))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        for score, _resource_id, resource, reasons in ranked[:per_type_limit]:
            items.append({
                "resourceType": resource_type,
                "resourceId": resource.id,
                "title": resource.title,
                "score": score,
                "reasons": reasons,
                "region": getattr(resource, "region", ""),
                "deadline": resource.deadline.isoformat() if getattr(resource, "deadline", None) else None,
            })
    return {"items": items}


def create_career_plan(user, goal):
    profile = YouthProfile.objects.get(user=user)
    recommendations = match_resources(user, limit=1, goal=goal)["items"]
    recommended = {item["resourceType"]: item for item in recommendations}
    now = timezone.now()
    templates = [
        ("seven_days", "补全并确认个人成长画像", "update_profile", None, 2),
        ("seven_days", "查看一项与你匹配的有效政策", "view_policy", None, 4),
        ("seven_days", "收藏一个目标岗位或成长资源", "favorite_resource", "opportunity", 7),
        ("one_month", "完成一门目标技能课程", "complete_course", "course", 21),
        ("one_month", "参加一次县域青年实践活动", "enroll_activity", "activity", 30),
        ("one_month", "投递一个匹配岗位", "apply_opportunity", "opportunity", 30),
        ("three_months", "完成阶段成长复盘", "review_plan", None, 60),
        ("three_months", "更新画像并记录新增能力", "update_profile", None, 75),
        ("three_months", "执行下一轮政策与资源匹配", "resource_match", None, 90),
    ]
    with transaction.atomic():
        GrowthPlan.objects.filter(user=user, status=GrowthPlan.STATUS_ACTIVE).update(
            status=GrowthPlan.STATUS_REPLACED
        )
        plan = GrowthPlan.objects.create(
            user=user,
            goal=goal,
            ends_on=date.today() + timedelta(days=90),
            rationale={
                "region": profile.region,
                "education": profile.education,
                "major": profile.major,
                "intents": profile.intents,
                "abilities": profile.abilities,
            },
        )
        tasks = []
        for sequence, (stage, title, action_type, resource_type, due_days) in enumerate(templates, 1):
            resource = recommended.get(resource_type) if resource_type else None
            if resource:
                title = f"{title}：{resource['title']}"
            tasks.append(GrowthTask.objects.create(
                plan=plan,
                stage=stage,
                title=title,
                action_type=action_type,
                resource_type=resource_type or "",
                resource_id=resource["resourceId"] if resource else None,
                due_at=now + timedelta(days=due_days),
                sequence=sequence,
            ))
        GrowthEvent.objects.create(
            user=user,
            event_type="growth_plan_created",
            payload={"planId": plan.id, "goal": goal},
        )

    return {
        "planId": plan.id,
        "goal": plan.goal,
        "startsOn": plan.starts_on.isoformat(),
        "endsOn": plan.ends_on.isoformat(),
        "rationale": plan.rationale,
        "tasks": [
            {
                "taskId": task.id,
                "stage": task.stage,
                "title": task.title,
                "actionType": task.action_type,
                "resourceType": task.resource_type,
                "resourceId": task.resource_id,
                "dueAt": task.due_at.isoformat() if task.due_at else None,
                "status": task.status,
            }
            for task in tasks
        ],
    }
