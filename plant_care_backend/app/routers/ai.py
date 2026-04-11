from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter

from app.core.config import settings
from app.schemas import AiGenerateTasksRequest, AiGenerateTasksResponse, PlantTaskItem

router = APIRouter()


def _fallback_tasks(req: AiGenerateTasksRequest) -> dict[str, PlantTaskItem]:
    base = [
        "Check soil moisture",
        "Observe leaf condition",
        "Inspect for pests or disease",
        "Confirm light exposure is adequate",
        "Wipe leaves and clean the pot surface",
        "Record growth notes",
    ]
    if req.plant_state == "seedling":
        base.insert(1, "Avoid overwatering; keep soil slightly moist")
    if req.plant_state == "growing":
        base.insert(1, "Adjust watering frequency for this variety")
    if req.plant_state == "stable":
        base.insert(1, "Maintain a consistent care routine")
    base = base[: req.count]
    return {f"task_{i+1}": PlantTaskItem(content=base[i], state=False) for i in range(len(base))}


def _coerce_tasks(obj: Any) -> dict[str, PlantTaskItem] | None:
    if not isinstance(obj, dict):
        return None
    out: dict[str, PlantTaskItem] = {}
    for k, v in obj.items():
        if not isinstance(k, str):
            continue
        if not isinstance(v, dict):
            continue
        content = v.get("content")
        state = v.get("state", False)
        if not isinstance(content, str):
            continue
        out[k] = PlantTaskItem(content=content, state=bool(state))
    return out or None


def _extract_first_json_object(text: str) -> dict[str, Any] | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
    start = s.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_string:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                candidate = s[start : i + 1]
                try:
                    v = json.loads(candidate)
                except json.JSONDecodeError:
                    return None
                return v if isinstance(v, dict) else None
    return None


def _chat_completions_path(base_url: str) -> str:
    base = (base_url or "").strip().rstrip("/")
    if base.endswith("/v1"):
        return "/chat/completions"
    return "/v1/chat/completions"


@router.post("/generate_tasks", response_model=AiGenerateTasksResponse)
async def generate_tasks(req: AiGenerateTasksRequest) -> AiGenerateTasksResponse:
    if not settings.openai_api_key:
        return AiGenerateTasksResponse(tasks=_fallback_tasks(req))

    today_state = (req.today_state or "").strip()
    last_watering_time = (req.last_watering_time or "").strip()
    extra = ""
    if today_state:
        extra += f"今日狀況：{today_state}。"
    if last_watering_time:
        extra += f"上次澆水時間：{last_watering_time}。"

    prompt = (
        "You are a plant care assistant. Based on the plant variety, growth stage, today's condition, and last watering time, "
        "generate actionable daily care tasks that can be checked off."
        "Return a JSON object ONLY, in the format:"
        '{"task_1":{"content":"...","state":false},"task_2":{"content":"...","state":false}}.'
        f"Task count: {req.count}. Language: English. Locale: {req.locale}."
        f"Plant variety: {req.plant_variety}. Growth stage: {req.plant_state}."
        f"{extra}"
        "Return JSON only. Do not add any extra text."
    )

    try:
        async with httpx.AsyncClient(base_url=settings.openai_base_url, timeout=20.0) as client:
            r = await client.post(
                _chat_completions_path(settings.openai_base_url),
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                },
            )
        if r.status_code < 200 or r.status_code >= 300:
            return AiGenerateTasksResponse(tasks=_fallback_tasks(req))
        data = r.json()
    except (httpx.HTTPError, ValueError):
        return AiGenerateTasksResponse(tasks=_fallback_tasks(req))

    content = (
        (data.get("choices") or [{}])[0].get("message", {}).get("content")
        if isinstance(data, dict)
        else None
    )
    if not isinstance(content, str):
        return AiGenerateTasksResponse(tasks=_fallback_tasks(req))
    try:
        decoded = json.loads(content)
    except json.JSONDecodeError:
        decoded = _extract_first_json_object(content)
        if decoded is None:
            return AiGenerateTasksResponse(tasks=_fallback_tasks(req))
    tasks = _coerce_tasks(decoded)
    return AiGenerateTasksResponse(tasks=tasks or _fallback_tasks(req))
