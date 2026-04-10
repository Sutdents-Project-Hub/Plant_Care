# Plant Care Backend（FastAPI）

## 模組簡介
提供 APP 所需 API：JWT 登入/註冊與 token refresh、公告、植物與照護任務資料存取，並包含可選的 AI 任務產生端點（以環境變數設定 AI Key）。

## 使用技術
- FastAPI
- SQLAlchemy
- JWT（Bearer）
- PostgreSQL（部署建議）
- SQLite（本地快速測試用）
- Alembic（DB migration）
- OpenAI 相容 API（`/chat/completions`）

## 資料夾結構
- `app/main.py`：FastAPI 入口與 router 註冊
- `app/core/`：設定、DB、JWT
- `app/models.py`：資料表模型
- `app/schemas.py`：API request/response schema
- `app/routers/`：各功能路由

## 本地開發流程
- 建立虛擬環境與安裝套件（已在此環境驗證）
  - `cd plant_care_backend`
  - `python3 -m venv .venv`
  - `.venv/bin/pip install -r requirements.txt`
- 套用 DB migration（已在此環境以 SQLite 驗證）
  - `DATABASE_URL=sqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/python -m alembic upgrade head`
- 啟動 API（已在此環境驗證）
  - `DATABASE_URL=sqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000`
- 驗證 OpenAPI（已在此環境驗證）
  - `curl -s http://127.0.0.1:8000/openapi.json | head -n 5`

## 環境變數
參考：`.env.example`
- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ACCESS_TTL_MINUTES`
- `JWT_REFRESH_TTL_DAYS`
- `CORS_ALLOW_ORIGINS`
- `AI_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

## 建置 / 啟動方式
- 開發：使用 `uvicorn`
- 部署：使用 `Dockerfile` 建置 image 後啟動（此環境未啟動 Docker daemon，尚未完成 Docker 啟動驗證）
- 本地 Docker 測試：提供 `docker-compose.yml`（API + PostgreSQL）

## 部署細節
- 建議以環境變數注入 `JWT_SECRET` 與 `OPENAI_API_KEY`
- 容器啟動流程會先執行 Alembic migration，再啟動 API
- APP 端不保存 AI Key，僅由後端呼叫 AI 服務

## 常見問題
- 沒有設定 `OPENAI_API_KEY` 會怎樣？
  - `/api/v1/ai/generate_tasks` 會回傳內建的預設任務，避免前端功能中斷。
