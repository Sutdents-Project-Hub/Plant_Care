from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas import AiGenerateTasksRequest, AiGenerateTasksResponse, PlantTaskItem

router = APIRouter()


def _fallback_tasks(req: AiGenerateTasksRequest) -> dict[str, PlantTaskItem]:
    base = [
        "檢查土壤濕度",
        "觀察葉片狀態",
        "檢查是否有病蟲害",
        "確認光照是否充足",
        "清潔葉片與盆器表面",
        "記錄生長狀況",
    ]
    if req.plant_state == "seedling":
        base.insert(1, "避免過度澆水，保持微濕")
    if req.plant_state == "growing":
        base.insert(1, "依品種調整澆水頻率")
    if req.plant_state == "stable":
        base.insert(1, "維持固定照護節奏")
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


@router.post("/generate_tasks", response_model=AiGenerateTasksResponse)
async def generate_tasks(req: AiGenerateTasksRequest) -> AiGenerateTasksResponse:
    if not settings.openai_api_key:
        return AiGenerateTasksResponse(tasks=_fallback_tasks(req))

    prompt = (
        "你是一個植物照護助理。請根據植物品種與生長階段，產生可執行、具體、每日可勾選的照護任務。"
        "請用 JSON 物件回傳，格式為："
        '{"task_1":{"content":"...","state":false},"task_2":{"content":"...","state":false}}。'
        f"任務數量：{req.count}。語系：{req.locale}。"
        f"植物品種：{req.plant_variety}。生長階段：{req.plant_state}。"
        "只回傳 JSON，不要加任何說明文字。"
    )

    async with httpx.AsyncClient(base_url=settings.openai_base_url, timeout=20.0) as client:
        r = await client.post(
            "/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            },
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider error")
    data = r.json()
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
        return AiGenerateTasksResponse(tasks=_fallback_tasks(req))
    tasks = _coerce_tasks(decoded)
    return AiGenerateTasksResponse(tasks=tasks or _fallback_tasks(req))
