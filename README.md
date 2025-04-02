# Flask App 開發環境與伺服器架設指南

## 環境安裝與管理（使用 Pipenv）

本專案使用 `pipenv` 進行環境管理，請依照以下步驟設置：

### 1. 安裝 Pipenv（僅需首次執行）

```sh
pip install pipenv
```

### 2. 初始化環境（每次使用前執行）

```sh
pipenv install
```

### 3. 進入虛擬環境

```sh
pipenv shell
```

> 若專案內已有 `Pipfile`，將會自動同步安裝所有依賴。

### 4. 安裝與紀錄新依賴

```sh
pipenv install package_name
```

### 5. 退出虛擬環境

```sh
exit
```

### 6. 匯出依賴清單

```sh
pipenv requirements > requirements.txt
```

---

## 伺服器架設方案

### 內網架設

使用 `Python Flask` 啟動內網伺服器。

### 外網架設

使用 [`ngrok`](https://ngrok.com/) 暴露 Flask 伺服器。

### 固定網址

使用 [`Rebrandly`](https://www.rebrandly.com/) 提供穩定的對外連結。

---

## 伺服器啟動方式

### 1. 設置環境變數

請在 `.env` 中設置以下內容：

```python
REBRANDLY_API_KEY=000289fd396d44248b70567e2ac9dab4
REBRANDLY_LINK_ID=07c4e1aefb354771a5c4be8904ac0dae
NFROK_AUTH_TOKEN=2tfriendjn7OPP98aWS1j2mBrCN_2vNRGFCwj4ATujaFik4xC
```

註：PROJECT_ROOT會在初次import config時自動更新，不須手動填入

### 2. 啟動伺服器

請確保已進入 `pipenv shell` 環境：

```sh
python app.py
```

---

## .gitignore 說明

此檔案內指定的所有內容不會被上傳到github，目前包含兩個項目：

1. self/：為一個料夾，可以用來存放個人暫存用、實驗用檔案
2. .env：為一個環境檔，用來儲存api token, key等隱私資訊

---

## Rebrandly 設定資訊

* **短網址**：[`rebrand.ly/JohnnyDo-flask-app`](https://rebrand.ly/JohnnyDo-flask-app)
* **API Key**：`000289fd396d44248b70567e2ac9dab4`
* **Link ID**：`07c4e1aefb354771a5c4be8904ac0dae`

---

## Ngrok 設定資訊

* **Token**：`2tfriendjn7OPP98aWS1j2mBrCN_2vNRGFCwj4ATujaFik4xC`

---

## 配色規範


| 顏色   | HEX       |
| ------ | --------- |
| 深灰色 | `#282829` |
| 灰色   | `#434344` |
| 白色   | `#FFFFFF` |
| 淺灰色 | `#F5F5F7` |

---

## 注意事項

* 請勿在公開環境中洩漏 API 金鑰與 Token。
* 確保 `pipenv shell` 環境啟動後再執行 Flask 伺服器。

# Git 使用指南

## 初始化專案（僅限首次執行，之後禁止使用）

```sh
git init
git remote add origin <repository-url>
git branch -M main
git push --force origin main
```

> **⚠️ 注意**：`git push --force` 可能會覆蓋遠端分支，請謹慎使用！
> **🚫 之後請勿再執行 `git init` 或 `git push --force`**，避免影響遠端版本控制。
>
> repository-url：https://github.com/Manfred0829/Undergraduate-Project/tree/main

---

## 推送 (`push`) 變更

### 1. 建立新分支

```sh
git checkout -b new-branch-name
```


| 分支類型       | 命名規範                  | 例子                          |
| -------------- | ------------------------- | ----------------------------- |
| **主分支**     | `main`、`develop`         | `main`、`develop`             |
| **功能分支**   | `feature/描述`            | `feature/add-dark-mode`       |
| **修復分支**   | `bugfix/描述`、`fix/描述` | `bugfix/fix-memory-leak`      |
| **熱修復分支** | `hotfix/描述`             | `hotfix/security-patch`       |
| **釋出分支**   | `release/版本號`          | `release/v1.2.0`              |
| **測試/實驗**  | `experiment/描述`         | `experiment/new-db-structure` |
| **個人分支**   | `username/描述`           | `manfred/refactor-frontend`   |

### 2. 確認當前狀態（可選）

```sh
git status
```

### 3. 添加修改的檔案或資料夾

```sh
git add file-or-dir-name
```

> 如需添加所有變更：

```sh
git add .
```

### 4. 提交 (`commit`) 變更

```sh
git commit -m "清楚描述此次修改內容"
```

> **⚠️ 提交訊息需完整描述所有改動，避免不明確的內容！**

### 5. 推送 (`push`) 到遠端倉庫

```sh
git push origin new-branch-name
```

---

## 其他常用 Git 指令

### 查看當前分支

```sh
git branch
```

### 推送 feature 分支並設為 upstream

```sh
git push -u origin feature
```

> 推薦第一次使用，可以將本地的 main 分支與遠端的 origin/main 綁定。之後執行 git push 或 git pull 可以不需要指定 origin main。

### 移除在 staging area 的檔案

```sh
git reset HEAD <file>
```

> 在執行完 git add . 後，所有 modified files 會進入 staging area ，準備提交（commit）

### 還原本地檔案為遠端版本

```sh
git checkout -- <file>
```

### 取消追蹤檔案

```sh
git rm --cached your_file
```

> 讓 Git 不再追蹤檔案，但仍保留在工作目錄

### 刪除檔案

```sh
git rm -f your_file
```

> 連工作區的檔案一起刪除

### 切換分支

```sh
git checkout branch_name
```

### 創建分支並切換

```sh
git checkout -b branch_name
```

### 重新命名目前所在分支

```sh
git branch -M branch_name
```

### 從遠端的 main 分支拉取最新變更

```sh
git pull origin main
```

### 合併分支

```sh
git merge branch_name
```

---

## 注意事項

* **請勿直接推送至 `main` 分支**，請使用 **feature 分支** 提交變更，並透過 Pull Request (PR) 進行審查與合併。
* **提交訊息 (`commit message`) 應完整描述本次改動**，避免簡短或無意義的訊息，例如 `"update"` 或 `"fix"`。
* **使用 `git status` 檢查修改內容**，避免提交未預期的檔案。
