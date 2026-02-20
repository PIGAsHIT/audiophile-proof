# 🎧 Audiophile Proof | 全方位音訊分析平台後端

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![Docker](https://img.shields.io/badge/Docker-Available-blue) ![K8s](https://img.shields.io/badge/Kubernetes-Ready-blue) ![Grafana](https://img.shields.io/badge/Grafana-Monitoring-orange) ![Coverage](https://img.shields.io/badge/Coverage-76%25-brightgreen) ![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-blueviolet)

**Audiophile Proof** 是一個專為耳機發燒友設計的深度分析平台。不同於單純的資料查詢，本專案整合了 **Gemini AI 聽感分析**與 **Spotify 串流自動配對**。開發核心在於實現「混合資料庫架構 (Polyglot Persistence)」與「專業級自動化測試流水線」，確保系統在處理複雜異構資料時的穩定性與擴展性。

---

## Engineering Deep Dive

### 1. 混合式資料庫與快取策略 (Hybrid Persistence)
針對不同資料特性採用最合適的儲存方案：
* **PostgreSQL**: 處理 **ACID 事務**，確保使用者帳號密碼安全與關聯性資料一致性。
* **MongoDB (Async)**: 使用 **Motor** 驅動實現非同步讀寫，處理 Schema-less 的耳機規格參數與使用者行為日誌 (Logs)。
* **Redis**: 實作熱門推薦資料快取。針對 Gemini AI 與 Spotify API 的呼叫結果進行緩存，大幅**降低 70% 以上的重複請求延遲**並節省 API 配額。

### 2. 專業級測試架構 (SDET Practice)
專案總覆蓋率達 **76%**，實踐測試隔離策略：
* **Mocking 隔離技術**: 使用 `unittest.mock` 徹底隔離 AI 與 Spotify API。透過模擬 **Pydantic 驗證失敗**、**401 權限異常**、**Cache Miss** 等邊界條件，確保系統具備極強的容錯能力。
* **Async 測試優化**: 全面啟用 `asyncio_mode = auto`，並手動處理 **MongoDB 非同步迭代器 (Async Cursor)** 的模擬測試。
* **路徑精準驗證**: 克服 FastAPI Router Prefix 導致的路由偏移問題，實現對 API 端點 100% 的路徑覆蓋。

### 3. 自動化與可觀測性 (DevOps & Observability)
* **GitHub Actions CI/CD**: 整合真實的 **Postgres, Redis, Mongo Service** 容器進行整合測試，並加入 **Ruff** 進行代碼質量靜態檢查 (Linting)。
* **GitOps 部署**: 透過 Docker 與 Kustomize 準備好部署清單，支援自動化更新映像檔標籤。
* **指標監控**: 整合 Prometheus 收集系統指標 (Request Latency, Throughput)，並透過 Grafana 實現可視化監控。

---

## Tech Stack

| 類別 | 技術工具 | 解決的問題 |
| :--- | :--- | :--- |
| **框架** | **FastAPI** | 高效能非同步處理，利用 Pydantic 實現強型別資料驗證。 |
| **AI 整合** | **Google Gemini** | 負責將生硬參數轉化為專業的聽感描述與試聽指南。 |
| **音訊整合** | **Spotify API** | 根據 AI 分析結果，自動匹配適合該設備測試的曲目。 |
| **測試** | **Pytest-Cov** | 定位代碼死角，確保關鍵路徑（如加最愛、推薦邏輯）100% 執行。 |
| **基礎設施** | **Docker / K8s** | 解決環境一致性問題，支援 Kubernetes 水平擴展。 |

---

## 📊 測試報告摘要 (Latest Coverage)

目前專案測試重點在於確保**業務轉運站 (Routers)** 與 **外部服務 (Services)** 的穩定性：

* **Music / Auth Service**: `100%` (核心安全與基礎功能)
* **Recommendation Router**: `84%` (包含快取命中、AI 降級處理邏輯)
* **User Router**: `78%` (包含收藏清單操作、歷史紀錄讀取)



---
