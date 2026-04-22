# Plant Care App

## 模組簡介
Flutter APP：提供登入/註冊、公告、植物管理、每日照護初始化、任務勾選同步，以及呼叫後端 AI 任務產生端點。
APP 端不保存任何 AI 金鑰，AI 設定由後端環境變數管理。

## 使用技術
- Flutter / Dart
- `http`
- `flutter_secure_storage`
- `url_launcher`

## 資料夾結構
- `lib/config/`：環境與 UI 常數（含 `API_BASE_URL`）
- `lib/services/`：後端 API 封裝與錯誤處理
- `lib/pages/`：UI 頁面與流程（登入、溫室、植物詳情等）
- `lib/utils/`：session、導航、日期與共用工具
- `lib/widgets/`：共用元件（按鈕、輸入框、loading）

## 本地開發流程
1) 安裝依賴

```bash
cd plant_care_app
flutter pub get
```

2) 靜態檢查與測試

```bash
flutter analyze
flutter test
```

## 環境變數
以編譯期參數注入：
- `API_BASE_URL`：後端 base URL
- 未提供時，Debug 預設 `http://localhost:8000`
- 未提供時，Release 預設 `https://plantcareapi.beioverworked.com`
- 需要切換環境時，仍可用 `--dart-define=API_BASE_URL=...` 覆寫

## 建置 / 啟動方式
### macOS（Debug）
啟動（需先啟動後端）：

```bash
flutter run -d macos --dart-define=API_BASE_URL=http://localhost:8000
```

僅建置（不啟動）：

```bash
flutter build macos --debug --dart-define=API_BASE_URL=http://localhost:8000
```

### Android（Release）
```bash
flutter build appbundle --release
```

### iOS（不簽章）
```bash
flutter build ios --release --no-codesign
```

## 部署細節
上架前請確認：
- Release 預設會連到 `https://plantcareapi.beioverworked.com`
- 若要改連其他環境，請在建置時明確帶入 `--dart-define=API_BASE_URL=...`
- APP 端不放置 `OPENAI_API_KEY` 等金鑰（由後端服務持有與呼叫 AI）
- Android release signing 使用 repo 外部的 `android/key.properties` 與 keystore；可參考 `android/key.properties.example`
- Android / iOS 正式識別已改為 `com.beioverworked.plantcare`

## 常見問題
- 登入狀態如何保存？
  - 使用 `flutter_secure_storage` 保存 `access_token` 與 `refresh_token`，並由 API 層在 `401` 時自動 refresh 後重試一次請求。
