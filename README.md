# Plant Care

## 專案名稱
Plant Care

## 專案簡介
本專案包含一個 Flutter APP（`plant_care_app`）與一個後端 API（`plant_care_backend`）。
後端提供 JWT 登入/註冊、公告、植物與照護任務資料存取，以及可選的 AI 任務產生功能（透過環境變數串接 OpenAI 相容 API）。

## 功能列表
- 使用者註冊 / 登入（`access token` + `refresh token`）
- 公告列表
- 植物建立 / 列表 / 每日初始化（今日狀態、最後澆水時間）
- 任務勾選與同步
- AI 任務產生（未設定 `OPENAI_API_KEY` 時回傳內建預設任務）

## 技術架構
- 前端：Flutter（Dart）
- 後端：FastAPI（Python）
- 資料庫：PostgreSQL（部署建議），SQLite（本機快速測試）
- 認證：JWT（Bearer）
- AI：OpenAI 相容 API（`/v1/chat/completions` 或 `/chat/completions`）

## 專案結構
- `plant_care_app/`：Flutter APP
- `plant_care_backend/`：FastAPI 後端

## 本地測試教學
### 後端（SQLite + Uvicorn）
1) 安裝依賴

```bash
cd plant_care_backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

2) 套用 migration

```bash
DATABASE_URL=sqlite+pysqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/python -m alembic upgrade head
```

3) 啟動 API

```bash
DATABASE_URL=sqlite+pysqlite:///./plant_care.db JWT_SECRET=dev-secret .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

4) 健康檢查

```bash
curl -s http://127.0.0.1:8000/health
```

5) 端到端 smoke 測試（不需要真的連 AI；未設定 `OPENAI_API_KEY` 時會走 fallback）

```bash
.venv/bin/python scripts/smoke_test.py
```

### 前端（Flutter）
1) 安裝依賴與靜態檢查

```bash
cd plant_care_app
flutter pub get
flutter analyze
flutter test
```

2) 啟動（macOS）

```bash
flutter run -d macos --dart-define=API_BASE_URL=http://localhost:8000
```

## 環境變數
### 前端（編譯期參數）
- `API_BASE_URL`：後端 base URL（預設 `http://localhost:8000`）

### 後端（建議以環境變數或 `.env` 注入）
參考：`plant_care_backend/.env.example`
- `DATABASE_URL`：資料庫連線字串
- `JWT_SECRET`：JWT 簽章密鑰
- `JWT_ACCESS_TTL_MINUTES`：access token 存活時間（分鐘）
- `JWT_REFRESH_TTL_DAYS`：refresh token 存活時間（天）
- `CORS_ALLOW_ORIGINS`：允許的前端來源（以逗號分隔或 `*`）
- `OPENAI_API_KEY`：AI 供應商金鑰（可留空，後端會自動回傳 fallback 任務）
- `OPENAI_BASE_URL`：OpenAI 相容 API base URL
- `OPENAI_MODEL`：使用的模型名稱（預設 `gpt-4o-mini`）

## Coolify 部署教學
### 後端服務
- Build context：`plant_care_backend`
- Dockerfile：`plant_care_backend/Dockerfile`
- Exposed port：`8000`
- Healthcheck path：`/health`

### 建議的後端環境變數
- 必填：`DATABASE_URL`、`JWT_SECRET`
- 建議：`CORS_ALLOW_ORIGINS`（正式環境請不要用 `*`）
- 可選（AI）：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`

### AI 串接與更換供應商
- 本專案後端使用「OpenAI 相容協定」呼叫 AI，因此只要供應商支援該協定即可透過調整 `OPENAI_BASE_URL` 切換。
- 例：`OPENAI_BASE_URL=https://free.v36.cm` 或 `OPENAI_BASE_URL=https://api.v36.cm`

## 前端 / 後端詳細文件連結
- 前端：[plant_care_app/README.md](file:///Users/felix/Documents/Flutter%20%E6%95%99%EAD%B8/Max/Plant_Care/plant_care_app/README.md)
- 後端：[plant_care_backend/README.md](file:///Users/felix/Documents/Flutter%20%E6%95%99%EAD%B8/Max/Plant_Care/plant_care_backend/README.md)
