# iimoo Backstage Demo 版本

這是一個演示版本，不會實際操作 GitHub 倉庫，適合用於展示和測試功能。

## 功能特色

- 🎭 **完全模擬模式**: 所有 Git 操作都是模擬的，不會影響真實的 GitHub 倉庫
- 📁 **本地資料儲存**: 作品集資料保存在本地 `resources/demo-portfolio` 資料夾
- 🖼️ **圖片模擬**: 上傳的圖片會創建為演示檔案
- 🔒 **安全測試**: 可以安全地測試所有功能而不擔心資料遺失

## 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 啟動 Demo 伺服器
```bash
python app_demo.py
```

### 3. 登入系統
- 網址: http://localhost:5000
- 登入密碼: `demo123`

## Demo 模式說明

### Git 操作模擬
- `git clone`: 創建本地 demo 資料夾結構
- `git pull`: 模擬拉取最新變更
- `git add`: 模擬暫存檔案
- `git commit`: 模擬提交變更
- `git push`: 模擬推送到遠端

### 作品集管理
- 創建新作品集: 資料保存在 `resources/demo-portfolio/`
- 更新作品集: 修改本地 JSON 檔案
- 刪除作品集: 移除本地資料夾
- 圖片上傳: 創建演示檔案

### 預設 Demo 資料
系統會自動創建兩個示範作品集

## 檔案結構

```
demo/
├── app_demo.py              # Demo 主應用程式
├── git_operations_demo.py   # Git 操作模擬
├── portfolio_manager_demo.py # 作品集管理模擬
├── resources/
│   └── demo-portfolio/      # Demo 作品集資料
└── templates/               # 網頁模板
```

## 環境變數

Demo 模式不需要真實的 GitHub 設定，但可以設定以下變數:

```bash
# 可選的環境變數
PORT=5000                    # 伺服器埠號
ADMIN_PASSWORD=demo123       # 管理員密碼
SECRET_KEY=demo-secret-key   # Flask session 密鑰
```

## 與正式版本差異

| 功能 | 正式版本 | Demo 版本 |
|------|----------|-----------|
| Git 操作 | 真實 GitHub API | 模擬操作 |
| 資料儲存 | GitHub 倉庫 | 本地檔案 |
| 圖片處理 | 真實圖片 | 演示檔案 |
| 安全性 | 需要 GitHub Token | 無需 Token |
| 用途 | 生產環境 | 展示/測試 |

## 注意事項

1. **資料持久性**: Demo 資料只存在於本地，重啟伺服器後會重新初始化
2. **圖片顯示**: 由於是演示檔案，圖片可能無法正常顯示
3. **效能**: 模擬操作包含延遲，模擬真實網路環境
4. **備份**: Demo 資料不會自動備份，請注意資料安全

## 切換到正式版本

如需使用正式版本，請:
1. 切換到 `master` 分支
2. 設定真實的 GitHub Token 和倉庫 URL
3. 使用 `python app.py` 啟動

## 故障排除

### 常見問題

**Q: 無法登入**
A: 確認使用密碼 `demo123`

**Q: 作品集不顯示**
A: 檢查 `resources/demo-portfolio` 資料夾是否存在

**Q: 圖片上傳失敗**
A: 確認檔案格式為 JPG 或 WebP

### 重新初始化 Demo 資料

刪除 `resources/demo-portfolio` 資料夾，重啟伺服器即可重新初始化。 