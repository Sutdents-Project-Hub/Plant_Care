# Plant Care

## 專案簡介
本專案包含一個 Flutter APP（`plant_care_app`）與一個後端 API（`plant_care_backend`）。後端提供 JWT token 登入/註冊、植物與任務資料存取，以及可選的 AI 任務產生功能（以環境變數設定 AI Key）。

## 功能列表
- 使用者註冊 / 登入（`access token` + `refresh token`）
- 公告列表
- 植物建立 / 列表 / 每日初始化（今日狀態、最後澆水時間）
- 任務勾選與同步
- AI 任務產生（未設定 AI Key 時會回傳內建預設任務）

## 技術架構
- 前端：Flutter（Dart）
- 後端：FastAPI（Python）
- 資料庫：PostgreSQL（部署建議），SQLite（本地快速測試用）
- 認證：JWT（Bearer）
- AI：OpenAI 相容 API（由後端以環境變數設定）

## 專案結構
- `plant_care_app/`：Flutter APP
- `plant_care_backend/`：FastAPI 後端

## 本地測試教學
- 後端（已在此環境驗證）
  - `cd plant_care_backend`
  - `python3 -m venv .venv`
  - `.venv/bin/pip install -r requirements.txt`
  - `DATABASE_URL=sqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/python -m alembic upgrade head`
  - `DATABASE_URL=sqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - `curl -s http://127.0.0.1:8000/openapi.json | head -n 5`
- 前端（已在此環境驗證）
  - `cd plant_care_app`
  - `flutter pub get`
  - `flutter analyze`

## 環境變數
- 後端（建議用 `.env`）
  - 參考：`plant_care_backend/.env.example`
- 前端（編譯期參數）
  - `API_BASE_URL`：後端 base URL（預設 `http://localhost:8000`）

## Coolify 部署教學
後端建議用 Dockerfile 方式部署，並搭配 Coolify 提供的 PostgreSQL。
- 後端服務
  - Build context：`plant_care_backend`
  - Dockerfile：`plant_care_backend/Dockerfile`
  - Port：`8000`
  - Healthcheck：`/health`
- PostgreSQL
  - 在 Coolify 建立 PostgreSQL 後，將連線字串填入後端的 `DATABASE_URL`
- 必要環境變數（後端）
  - 參考：`plant_care_backend/.env.example`
  - 最少需要：`DATABASE_URL`、`JWT_SECRET`
- 注意事項
  - `JWT_SECRET` 請使用強隨機字串，且不要提交到 repo
  - 若 `OPENAI_API_KEY` 未設定，AI 任務端點會回傳預設任務以確保 APP 不中斷

## 前端 / 後端詳細文件連結
- 前端：plant_care_app/README.md
- 後端：plant_care_backend/README.md
