# Portfolio Manager Web UI

使用 Flask 建立的 Web 後台應用，用來管理我為iimoo設計公司架設在 GitHub Page 的官網。

## 功能

*   上傳作品集圖片 (JPG 格式)。
![iimoo-後台](https://github.com/Alan-Cheng/Iimoo-Design-Portfolio-Manager-Web-UI/blob/master/demo/upload.png?raw=true "上傳頁面")
>
*   透過 Web UI 新增、編輯、刪除作品集。
*   自動處理第一張上傳圖片 (`0.jpg`)，根據第二張圖片 (`1.jpg`) 的尺寸進行裁剪、縮放和置中。
在對作品集進行增刪改操作後，自動將變更 (圖片和描述檔 `portfolio_description.json`) add、commit 並 push 到指定的 GitHub Repo。
![iimoo-後台](https://github.com/Alan-Cheng/Iimoo-Design-Portfolio-Manager-Web-UI/blob/master/demo/portfolio.png?raw=true "作品頁面")
>
*   編輯作品集描述資訊 (專案名、描述、區域、日期、坪數、種類)。
![iimoo-後台](https://github.com/Alan-Cheng/Iimoo-Design-Portfolio-Manager-Web-UI/blob/master/demo/edit.png?raw=true "編輯頁面")
>
*   以 Docker 容器化部署，提供該公司員工自行操作。

## 環境需求

*   Python 3.9 或更高版本
*   pip (Python 套件安裝器)
*   Git
*   Docker
*   GitHub Personal Access Token (PAT)，具有讀寫目標倉庫的權限。

## 本地端設定與執行

1.  **Clone:**
    手動 clone `Alan-Cheng/《YourGitHubRepoName》` 倉庫到專案根目錄下的 `resources/` 資料夾中，或者讓應用程式在首次啟動時自動 clone。
    ```bash
    # (如果手動 Clone)
    mkdir resources
    git clone https://github.com/Alan-Cheng/《YourGitHubRepoName》 resources/《YourGitHubRepoName》
    ```

2.  ** `.env` 檔案:**
    在專案根目錄建立一個名為 `.env` 的檔案用於測試環境，填入 GitHub Token：
    ```dotenv
    GITHUB_TOKEN=《YourGitHubPersonalAccessTokenHere》
    GITHUB_REPO_URL=《YourGitHubRepoURL》
    GITHUB_REPO_NAME=《YourGitHubRepoName》
    ```
    **重要:**  `ghp_YourGitHubPersonalAccessTokenHere` 替換為有存取權限的 Token。

3.  **測試環境安裝依賴套件:**
    打開終端機，進入專案根目錄，執行：
    ```bash
    pip install -r requirements.txt
    ```

4.  **執行應用程式:**
    ```bash
    python app.py
    ```
    應用程式啟動時會檢查 `resources/《YourGitHubRepoName》` 是否存在，若不存在會嘗試自動 clone。

5.  **應用程式:**
    打開瀏覽器，輸入 `http://localhost:5000`。

## Docker 設定與執行

1.  **建置 Docker 映像檔:**
    在包含 `Dockerfile` 的專案根目錄中，執行：
    ```bash
    docker build -t portfolio-manager-app .
    ```

2.  **執行 Docker 容器:**
    *   將 `your_actual_github_token` 替換為您的 GitHub Personal Access Token。
    *   執行以下指令：
    ```bash
    # 將 your_actual_github_token 替換成你的 GitHub PAT
    docker run -p 5000:5000 -e GITHUB_TOKEN=《YourGitHubPersonalAccessTokenHere》 -e GITHUB_REPO_URL=《YourGitHubRepoURL》 -e GITHUB_REPO_NAME=《YourGitHubRepoName》 --name portfolio-app portfolio-manager-app

    ```
    *   `-p 5000:5000`: 將主機的 Port 5000 映射到容器的 Port 5000。
    *   `-e GITHUB_TOKEN="..."`: **必須**透過環境變數將您的 GitHub Token 傳遞給容器。
    *   `-e GITHUB_REPO_URL="..."`: **必須**透過環境變數將您的 GitHub Repo URL 傳遞給容器。
    *   `-e GITHUB_REPO_NAME="..."`: **必須**透過環境變數將您的 GitHub Repo Name 傳遞給容器。
    *   `--name portfolio-app`: 為容器命名，方便管理 (例如停止 `docker stop portfolio-app`, 移除 `docker rm portfolio-app`)。

3.  **使用方式:**
    啟動容器並稍等片刻，容器啟動時會自動 clone 需要一點時間。打開瀏覽器，輸入 `http://localhost:5000`。

## 注意事項

*   **圖片處理:** 上傳新作品集或替換圖片時，若同時存在 `0.jpg` 和 `1.jpg`，程式會嘗試處理 `0.jpg` 使其符合 `1.jpg` 的畫布大小。此功能依賴 Pillow 套件。
*   **自動同步:** 對作品集的增刪改操作會觸發背景程序，自動執行 `git pull`, `git add .`, `git commit`, `git push`。您可以在執行 Flask 應用程式的終端機中看到相關的 Git 操作訊息。