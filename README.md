# 🎧 Audiophile Proof API | 高傳真音訊分析平台後端

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![Docker](https://img.shields.io/badge/Docker-Available-blue) ![K8s](https://img.shields.io/badge/Kubernetes-Ready-blue) ![Grafana](https://img.shields.io/badge/Grafana-Monitoring-orange)

**Audiophile Proof** 是一個專為耳機發燒友打造的後端系統，旨在解決音訊設備規格繁雜、數據分散的問題。本專案採用現代化 **Microservices-ready** 架構，結合混合資料庫設計（Hybrid Database Pattern）與完整 DevOps 流水線，實現高併發、低延遲的資料查詢與推薦服務。

## 💡 專案亮點 (Key Highlights)

* **混合資料庫架構 (Polyglot Persistence)**：
    * 針對 **交易一致性 (ACID)** 需求（如使用者帳號、權限），採用 **PostgreSQL**。
    * 針對 **非結構化/半結構化資料**（如多變的耳機規格、評論），採用 **MongoDB**。
    * 針對 **高頻讀取**（如熱門推薦、Session），採用 **Redis** 進行快取。
* **高效能非同步處理**：基於 **FastAPI (ASGI)** 框架與 **Motor (Async Mongo driver)**，充分利用 Python `asyncio` 特性，提升 I/O 密集型任務的吞吐量。
* **全方位可觀測性 (Observability)**：
    * 整合 **Prometheus** 收集系統指標 (Request Latency, Throughput)。
    * 使用 **Grafana** 建構視覺化監控儀表板，即時掌握 API 健康狀態。
* **DevOps 最佳實踐**：
    * 完整容器化 (Dockerized) 環境。
    * CI/CD Pipeline (GitHub Actions + ArgoCD) 自動化部署至 Kubernetes (Minikube)。
* **安全性設計**：整合 JWT (JSON Web Tokens) 身份驗證與 Pydantic 資料驗證，確保 API 安全與資料格式正確。

## 🛠️ 技術堆疊 (Tech Stack)

| 類別 | 技術/工具 | 用途說明 |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | 高效能 Web 框架，自動生成 Swagger 文件 |
| **SQL DB** | **PostgreSQL** | 儲存使用者資料 (User Auth)、關聯性資料 |
| **NoSQL DB** | **MongoDB** | 儲存耳機詳細規格 (Schema-less)、操作 Log |
| **Cache** | **Redis** | 資料快取、Rate Limiting 基礎 |
| **Container** | **Docker & Compose** | 應用程式容器化與本地編排 |
| **Orchestration** | **Kubernetes (Minikube)** | 容器調度與管理 |
| **CI/CD** | **GitHub Actions / ArgoCD** | 持續整合與 GitOps 部署流程 |
| **Monitoring** | **Prometheus & Grafana** | 系統指標收集與視覺化儀表板 |

## 📂 系統架構與目錄結構

本專案採用分層式架構 (Layered Architecture)，將路由、商業邏輯與資料存取層分離，並透過依賴注入 (Dependency Injection) 管理資料庫連線。

```text
.
├── infra/               # 基礎設施層 (IaC)
│   ├── docker-compose.yml   # 本地開發環境編排
│   └── k8s/                 # Kubernetes Manifests (Deployment, Service)
├── src/                 # 應用程式核心
│   ├── core/            # 全域配置 (Config, Security)
│   ├── db/              # 資料庫連線工廠 (Postgres, Mongo, Redis)
│   ├── models/          # SQLAlchemy ORM 定義 (SQL)
│   ├── schemas/         # Pydantic 資料驗證模型 (DTOs)
│   ├── services/        # 核心商業邏輯 (Business Logic)
│   ├── routers/         # API 路由控制器 (Controllers)
│   └── main.py          # 程式進入點 (Application Entrypoint)
├── tests/               # 單元測試與整合測試
├── Dockerfile           # 容器建置腳本
└── requirements.txt     # Python 依賴清單

