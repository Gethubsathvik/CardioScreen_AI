# 🫀 CardioScreen AI

> **CardioScreen AI**: Compares six ML models on the Cleveland heart-disease data, **automatically selects the best by cross-validation**, and serves it through a REST API and a web UI with per-patient explanations.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### One-liner Setup
```bash
git clone https://github.com/Gethubsathvik/CardioScreen_AI.git
cd CardioScreen_AI
pip install -r requirements-dev.txt
python -m cardioscreen serve
```

### Run the Project
```bash
# 1️⃣ Train models (auto-selects best via 5-fold CV)
python -m cardioscreen train

# 2️⃣ Start API server + Web UI
python -m cardioscreen serve
# 🌐 Open http://127.0.0.1:8000
# 📚 Swagger docs at http://127.0.0.1:8000/docs
```

### Run Tests
```bash
python -m pytest -q
```

### CLI Prediction
```bash
python -m cardioscreen predict \
  --age 58 --sex 1 --cp 0 --trestbps 140 --chol 240 \
  --fbs 0 --restecg 1 --thalach 122 --exang 1 \
  --oldpeak 2 --slope 1 --ca 1 --thal 3
```

---

## 🖥️ Platform-Specific Instructions

| Platform | Command | Notes |
|----------|---------|-------|
| **🪟 Windows (PowerShell)** | `.\.venv\Scripts\Activate.ps1` then commands above | Use `python` not `python3` |
| **🐧 Linux / 🍎 macOS** | `source .venv/bin/activate` then commands above | Ensure `python3` and `venv` installed |
| **🤖 Android (Termux)** | `pkg install python git` → `pip install -r requirements-dev.txt` | Limited memory; skip training, use pre-trained model |
| **🐳 Docker (Any OS)** | `docker build -t cardioscreen . && docker run -p 8000:8000 cardioscreen` | Production-ready container |

### Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Then install deps
pip install --upgrade pip
pip install -r requirements-dev.txt
```

---

## 🏗️ Architecture Overview

### 📁 Project Structure (MVC + Service Layer + Feature-Based)

```
CardioScreen_AI/
├── 📁 cardioscreen/                 # Main package (MVC + Services)
│   ├── 📁 api/                      # 🎮 Controller Layer (FastAPI routes)
│   │   ├── routes/
│   │   │   ├── health.py            # GET /health
│   │   │   ├── model_info.py        # GET /api/model
│   │   │   ├── predict.py           # POST /predict, /predict/batch
│   │   │   └── features.py          # GET /api/features
│   │   ├── middleware/
│   │   │   └── validation.py        # Request validation middleware
│   │   └── __init__.py              # FastAPI app factory
│   │
│   ├── 📁 services/                 # 🔧 Service Layer (Business Logic)
│   │   ├── model_service.py         # Model loading, prediction, explanation
│   │   ├── training_service.py      # Training pipeline, CV, model selection
│   │   ├── data_service.py          # Data loading, preprocessing, validation
│   │   └── explanation_service.py   # Occlusion-based local explanations
│   │
│   ├── 📁 models/                   # 🧠 Domain Models (Data Structures)
│   │   ├── schemas.py               # Pydantic models (Request/Response)
│   │   ├── domain.py                # Core domain entities
│   │   └── enums.py                 # Risk bands, feature types
│   │
│   ├── 📁 features/                 # 🎯 Feature-Based Modules
│   │   ├── patient/                 # Patient feature module
│   │   │   ├── repository.py        # Data access
│   │   │   ├── service.py           # Business logic
│   │   │   └── schemas.py           # Feature-specific schemas
│   │   ├── clinical/                # Clinical features module
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   └── risk/                    # Risk assessment module
│   │       ├── calculator.py
│   │       ├── bands.py
│   │       └── schemas.py
│   │
│   ├── 📁 core/                     # ⚙️ Core Infrastructure
│   │   ├── config.py                # Settings management (Pydantic Settings)
│   │   ├── exceptions.py            # Custom exceptions
│   │   ├── logging.py               # Structured logging config
│   │   └── security.py              # API keys, rate limiting (future)
│   │
│   ├── 📁 utils/                    # 🛠️ Shared Utilities
│   │   ├── metrics.py               # Evaluation metrics
│   │   ├── serialization.py         # Model save/load (joblib)
│   │   └── validators.py            # Custom validators
│   │
│   ├── train.py                     # 🎯 Training CLI entry point
│   ├── predictor.py                 # 🔮 Prediction logic
│   ├── data.py                      # 📊 Data loading/preprocessing
│   ├── __main__.py                  # 🖥️ CLI dispatcher
│   └── __init__.py
│
├── 📁 static/                       # 🌐 Frontend (Static Files)
│   ├── index.html                   # Main UI
│   ├── styles.css                   # Extracted styles
│   └── app.js                       # Extracted JavaScript
│
├── 📁 tests/                        # 🧪 Test Suite (Feature-based)
│   ├── unit/
│   │   ├── test_services/
│   │   ├── test_features/
│   │   └── test_core/
│   ├── integration/
│   │   ├── test_api/
│   │   └── test_training_pipeline.py
│   └── fixtures/
│
├── 📁 models/                       # 💾 Trained Models (gitignored)
│   └── heart_model.joblib
│
├── 📁 data/                         # 📊 Datasets
│   └── heart.csv
│
├── 📁 reports/                      # 📈 Generated Reports
│   ├── metrics.json
│   └── model_comparison.csv
│
├── 📁 docs/                         # 📚 Documentation
│   ├── DATA_NOTES.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── archive/
│
├── 📁 deployment/                   # 🚀 Deployment Configs
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── .dockerignore
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── github-actions/
│       └── ci-cd.yml
│
├── 📁 legacy/                       # 🗃️ Legacy Scripts (Reference)
│
├── requirements.txt                 # Runtime dependencies
├── requirements-dev.txt             # Dev dependencies
├── pyproject.toml                   # Build config
├── .gitignore
├── LICENSE
├── Makefile                         # Common commands
└── README.md
```

---

### 🔄 MVC + Service Layer Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  Controller │────▶│   Service   │────▶│   Model     │
│  (Browser/  │     │  (API       │     │  (Business  │     │  (Domain/   │
│   CLI)      │     │   Routes)   │     │   Logic)    │     │   ML Model) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                    │                    │
                           ▼                    ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                    │ Validation  │     │  Features   │     │  Data       │
                    │ Middleware  │     │  Modules    │     │  Repository │
                    └─────────────┘     └─────────────┘     └─────────────┘
```

**Key Principles:**
- **Controllers** (`api/routes/`) → Handle HTTP, validation, serialization
- **Services** (`services/`) → Pure business logic, testable in isolation
- **Models** (`models/`) → Data structures, Pydantic schemas, ML artifacts
- **Features** (`features/`) → Domain-driven modules (patient, clinical, risk)

---

### 🏗️ Microservices Architecture (Future-Ready)

The codebase is structured for **gradual extraction to microservices**:

| Service | Responsibility | API Contract | Data Store |
|---------|---------------|--------------|------------|
| **🏥 Patient Service** | Patient CRUD, demographics | `/api/v1/patients` | PostgreSQL |
| **🔬 Clinical Service** | Clinical features, vitals | `/api/v1/clinical` | PostgreSQL |
| **🧠 ML Inference Service** | Model serving, predictions | `/api/v1/infer` | Model Registry (S3/GCS) |
| **📊 Risk Service** | Risk calculation, bands | `/api/v1/risk` | Redis (cache) |
| **📝 Explanation Service** | SHAP/LIME explanations | `/api/v1/explain` | - |
| **🎓 Training Service** | Model training, CI/CD | `/api/v1/train` | MLflow/Weights&Biases |

**Current State**: All services run in-process (monolith). Each `features/` module maps 1:1 to a future microservice.

**Migration Path:**
1. ✅ Feature modules with clear boundaries
2. 🔄 Extract `services/` to separate processes (gRPC/REST)
3. 🔄 Add API Gateway (Kong/Traefik)
4. 🔄 Implement service discovery, circuit breakers
5. 🔄 Deploy to Kubernetes (see `deployment/kubernetes/`)

---

## 🤖 ML Algorithms & Formulas

### 1️⃣ Preprocessing
**Standardisation (z-score)** for Logistic Regression, SVM, KNN — fitted on training data only via `Pipeline`:

$$z = \frac{x - \mu_{train}}{\sigma_{train}}$$

Tree-based models (Random Forest, Gradient Boosting, Decision Tree) don't require scaling.

---

### 2️⃣ Classification Models (6 Compared)

| Model | Core Idea | Key Formula |
|-------|-----------|-------------|
| **Logistic Regression** | Linear probability via sigmoid; L2-regularised | $P(y=1\mid x)=\frac{1}{1+e^{-(w^\top x+b)}}$, Loss $=-\sum[y\log p+(1-y)\log(1-p)]+\frac{1}{2C}\lVert w\rVert^2$ |
| **SVM (RBF Kernel)** | Max-margin in kernel space | $K(x,x')=e^{-\gamma\lVert x-x'\rVert^2}$, $f(x)=\sum_i\alpha_i y_i K(x_i,x)+b$ |
| **Random Forest** | Ensemble of bootstrap trees | $\hat p(x)=\frac{1}{T}\sum_{t=1}^{T}p_t(x)$ |
| **Gradient Boosting** | Sequential error correction | $F_m(x)=F_{m-1}(x)+\eta\,h_m(x)$ |
| **K-Nearest Neighbours** | Majority vote of *k* neighbours | $d(x,x')=\sqrt{\sum_j (x_j-x'_j)^2}$ |
| **Decision Tree** | Greedy impurity reduction | Gini $=1-\sum_k p_k^2$ |

---

### 3️⃣ Model Selection & Tuning
- **Stratified 5-fold CV** — preserves class ratio per fold
- **Grid Search** — hyperparameter tuning per model
- **Primary Metric**: **ROC-AUC** (threshold-independent)
- **Selection**: Highest CV-AUC on training split → **test set never influences choice**
- **Final Evaluation**: Single hold-out test set (20%, 61 patients)

---

### 4️⃣ Evaluation Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Accuracy** | $\frac{TP+TN}{TP+TN+FP+FN}$ | Overall correctness |
| **Precision** | $\frac{TP}{TP+FP}$ | Avoid false alarms |
| **Recall (Sensitivity)** | $\frac{TP}{TP+FN}$ | **Catch sick patients** ⭐ |
| **Specificity** | $\frac{TN}{TN+FP}$ | Avoid false reassurance |
| **F1-Score** | $\frac{2\cdot P\cdot R}{P+R}$ | Balance P/R |
| **ROC-AUC** | $\int_0^1 TPR(FPR)\,dFPR$ | Ranking quality |
| **Brier Score** | $\frac{1}{N}\sum(p_i-y_i)^2$ | Probability calibration |

> **Clinical Priority**: Sensitivity > Specificity (missing disease is costlier than false alarm)

---

### 5️⃣ Prediction & Explanation
- **Decision Threshold**: $P(\text{disease}) \ge 0.5$
- **Risk Bands**: Low < 0.33 ≤ Moderate < 0.66 ≤ High
- **Local Explanation (Occlusion)**:
  $$\text{effect}_j = P(x) - P(x_{j\rightarrow \text{median}})$$
  Positive = feature increases risk. Top 5 shown in UI.

---

### 6️⃣ Data Handling
- **Deduplication**: Exact duplicates removed *before* split (1,025 → 302 patients)
- **Stratified Split**: 80/20, `random_state=42`
- **Validation**: Pydantic schemas with clinical range checks

---

## 🌐 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/model` | GET | Model metadata (name, metrics) |
| `/api/features` | GET | Feature specs for UI forms |
| `/predict` | POST | Single prediction + explanation |
| `/predict/batch` | POST | Batch (≤1000) predictions |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc UI |

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":58,"sex":1,"cp":0,"trestbps":140,"chol":240,
       "fbs":0,"restecg":1,"thalach":122,"exang":1,
       "oldpeak":2.0,"slope":1,"ca":1,"thal":3}'
```

---

## 🎬 Demo

### Web UI Screenshot
![CardioScreen AI Demo](docs/assets/demo-screenshot.png)

> **📸 Add your screenshot**: Place a PNG at `docs/assets/demo-screenshot.png` (recommended: 1200×800px)

### Features Shown
- ✅ Dynamic form from `/api/features`
- ✅ Risk gauge with color-coded bands
- ✅ "What drove this prediction" waterfall bars
- ✅ Clinical dropdowns with proper labels
- ✅ Example patient loader
- ✅ Responsive design (mobile/desktop)
- ✅ Dark mode support

---

## 🚀 GitHub Deployment

### Quick Setup (if you've done this before)
```bash
# 1. Create repo on GitHub (or use existing)
# 2. Push local code
git init
git add .
git commit -m "feat: initial CardioScreen AI commit"
git branch -M main
git remote add origin https://github.com/Gethubsathvik/CardioScreen_AI.git
git push -u origin main
```

### First Time? Step-by-Step

#### 🪟 Windows
```powershell
# Install Git: https://git-scm.com/download/win
# Open PowerShell as Administrator
winget install Git.Git

# Clone & setup
git clone https://github.com/Gethubsathvik/CardioScreen_AI.git
cd CardioScreen_AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

#### 🐧 Linux / 🍎 macOS
```bash
# Install Git
sudo apt install git        # Ubuntu/Debian
brew install git            # macOS

# Clone & setup
git clone https://github.com/Gethubsathvik/CardioScreen_AI.git
cd CardioScreen_AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

#### 🐳 Docker (All Platforms)
```bash
# Build
docker build -t cardioscreen-ai .

# Run
docker run -d -p 8000:8000 --name cardioscreen cardioscreen-ai

# Or with docker-compose
docker-compose up -d
```

---

### 🔄 CI/CD Pipeline (GitHub Actions)

The repo includes `.github/workflows/ci-cd.yml` with:

```yaml
# On every push/PR:
- ✅ Lint (ruff, black --check)
- ✅ Type check (mypy)
- ✅ Unit tests (pytest)
- ✅ Integration tests
- ✅ Build Docker image
- ✅ Push to GHCR (on main branch)
- ✅ Deploy to staging (on main branch)
```

**Required Secrets (GitHub Settings → Secrets):**
| Secret | Description |
|--------|-------------|
| `DOCKER_REGISTRY_TOKEN` | GHCR/GitHub Packages token |
| `STAGING_KUBECONFIG` | Base64-encoded kubeconfig |
| `PROD_KUBECONFIG` | Base64-encoded kubeconfig (manual approval) |

---

## 📦 Makefile Commands

```bash
make help          # Show all commands
make install       # Install deps in venv
make train         # Train models
make serve         # Start server
make test          # Run tests
make lint          # Lint + format check
make format        # Auto-format (black + ruff)
make typecheck     # Mypy type check
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make clean         # Remove cache, build artifacts
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## ⚠️ Disclaimer

> **Educational research project only.** Not a medical device. Not a substitute for professional medical advice, diagnosis, or treatment. Model trained on small single-cohort dataset (Cleveland, n=302). Not externally validated.

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open Pull Request

---

## 📚 References

- [Cleveland Heart Disease Dataset (UCI)](https://archive.ics.uci.edu/dataset/45/heart+disease)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

<p align="center">
  Made with ❤️ for cardiovascular health research
</p>#   C I   t r i g g e r 
 
 