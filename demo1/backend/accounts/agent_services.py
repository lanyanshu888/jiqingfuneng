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
