# Plant Care App（Flutter）

## 模組簡介
Flutter APP，提供登入/註冊、公告、植物管理、每日照護初始化、任務勾選，以及與後端 AI 任務產生端點整合。

## 使用技術
- Flutter / Dart
- `package:http`
- `flutter_secure_storage`

## 資料夾結構
- `lib/config/`：環境與 UI 常數（含 API base 設定）
- `lib/services/`：API 封裝與錯誤處理
- `lib/pages/`：各頁面 UI 與流程
- `lib/utils/`：session、日期與共用工具

## 本地開發流程
- 取得套件（已在此環境驗證）
  - `cd plant_care_app`
  - `flutter pub get`
- 靜態檢查（已在此環境驗證）
  - `flutter analyze`

## 環境變數
- `API_BASE_URL`
  - 作用：設定後端 base URL（預設 `http://localhost:8000`）
  - 設定方式：以編譯期參數 `--dart-define=API_BASE_URL=...` 注入（建議在 IDE 的 Run Configuration 設定）

## 建置 / 啟動方式
此段落需依你的目標平台（Android / iOS / Web）與本機裝置/模擬器狀況執行，尚未在此環境進行完整啟動驗證。

## 部署細節
APP 上架前請確認：
- 後端使用 `https`
- `API_BASE_URL` 指向正式環境
- 不在 APP 端放置任何 AI Key（由後端環境變數管理）

## 常見問題
- 登入狀態如何保存？
  - 使用 `flutter_secure_storage` 保存 `access_token` 與 `refresh_token`，並由 API 層在 `401` 時自動 refresh 後重試一次請求。
