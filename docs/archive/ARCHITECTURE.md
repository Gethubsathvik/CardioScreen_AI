# 🏗️ Architecture Document

**Project**: Heart Disease Predictor  
**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-11-21  
**Cycle**: 1 - SPECIFY (HIM-SPEC Three-Cycle Live Proof)

---

## 🎯 Architectural Vision

Build a **scalable, maintainable, and production-ready** machine learning platform for heart disease prediction that follows **Clean Architecture** principles, **Domain-Driven Design** patterns, and **Cloud-Native** best practices.

---

## 📐 Architectural Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Separation of Concerns** | Distinct layers for presentation, business logic, data | MVC + Service Layer |
| **Dependency Inversion** | High-level modules don't depend on low-level modules | Dependency Injection Container |
| **Single Responsibility** | Each module/class has one reason to change | Feature-based modules |
| **Open/Closed** | Open for extension, closed for modification | Plugin architecture for algorithms |
| **Interface Segregation** | Clients depend only on interfaces they use | Protocol-based contracts |
| **Composition over Inheritance** | Favor composition for flexibility | Service composition |

---

## 🏛️ High-Level Architecture

### Layered Architecture (MVC + Service)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   CLI App   │  │  REST API   │  │  Web UI     │  │  gRPC API   │        │
│  │  (Current)  │  │  (Planned)  │  │  (Planned)  │  │  (Planned)  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONTROLLER LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Application Controllers                           │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │PredictionCtrl│ │ TrainingCtrl │ │EvaluationCtrl│ │HealthCtrl  │  │   │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └─────┬──────┘  │   │
│  └─────────┼────────────────┼────────────────┼────────────────┼──────────┘   │
└────────────┼────────────────┼────────────────┼────────────────┼──────────────┘
             │                │                │                │
             ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICE LAYER                                    │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────┐  │
│  │  DataService   │ │ ModelService   │ │ EvalService    │ │PredService │  │
│  │                │ │                │ │                │ │            │  │
│  │ • load()       │ │ • train()      │ │ • evaluate()   │ │ • predict()│  │
│  │ • validate()   │ │ • tune()       │ │ • compare()    │ │ • batch()  │  │
│  │ • transform()  │ │ • register()   │ │ • report()     │ │ • explain()│  │
│  │ • split()      │ │ • version()    │ │ • visualize()  │ │ • log()    │  │
│  └───────┬────────┘ └───────┬────────┘ └───────┬────────┘ └─────┬──────┘  │
└──────────┼──────────────────┼──────────────────┼─────────────────┼──────────┘
           │                  │                  │                 │
           ▼                  ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DOMAIN LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Domain Entities                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Patient  │ │  Model   │ │Dataset   │ │Experiment│ │Metric    │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Domain Services                                 │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │Preprocessor  │ │  Trainer     │ │  Evaluator   │ │ Predictor  │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
           │                  │                  │                 │
           ▼                  ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Database   │ │  File Store │ │  Model Reg  │ │  Message    │          │
│  │  (Postgres) │ │  (MinIO/S3) │ │  (MLflow)   │ │  Bus (RMQ)  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Cache      │ │  Monitoring │ │  Logging    │ │  Config     │          │
│  │  (Redis)    │ │  (Prom/Graf)│ │  (ELK)      │ │  (Consul)   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Feature-Based Architecture

### Module Organization

```
src/
├── features/                    # Feature modules (vertical slices)
│   ├── data_ingestion/          # Data loading, validation, preprocessing
│   │   ├── domain/              # Entities, value objects, domain services
│   │   ├── application/         # Use cases, application services
│   │   ├── infrastructure/      # Repositories, external adapters
│   │   └── interfaces/          # Controllers, presenters, DTOs
│   ├── model_training/          # Training pipeline, algorithms
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── interfaces/
│   ├── model_evaluation/        # Evaluation, comparison, visualization
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── interfaces/
│   └── prediction/              # Inference, serving, explanation
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── interfaces/
├── shared/                      # Shared kernel (cross-cutting)
│   ├── kernel/                  # Base classes, interfaces, exceptions
│   ├── config/                  # Configuration management
│   ├── utils/                   # Common utilities
│   └── constants/               # Domain constants
└── core/                        # Application core
    ├── container.py             # DI container
    ├── application.py           # App bootstrap
    └── middleware/              # Cross-cutting concerns
```

### Feature Module Structure (Clean Architecture)

```
features/data_ingestion/
├── domain/
│   ├── entities/
│   │   ├── dataset.py
│   │   └── data_record.py
│   ├── value_objects/
│   │   ├── column_schema.py
│   │   └── validation_result.py
│   ├── services/
│   │   └── data_validator.py
│   └── repositories/
│       └── dataset_repository.py (interface)
├── application/
│   ├── use_cases/
│   │   ├── load_dataset.py
│   │   ├── validate_dataset.py
│   │   └── preprocess_dataset.py
│   ├── dto/
│   │   ├── load_dataset_request.py
│   │   └── dataset_response.py
│   └── services/
│       └── data_ingestion_service.py
├── infrastructure/
│   ├── repositories/
│   │   ├── csv_dataset_repository.py
│   │   └── postgres_dataset_repository.py
│   ├── external/
│   │   └── dvc_client.py
│   └── persistence/
│       └── dataset_orm.py
└── interfaces/
    ├── cli/
    │   └── data_commands.py
    ├── api/
    │   └── data_routes.py
    └── presenters/
        └── dataset_presenter.py
```

---

## ☁️ Microservices Architecture

### Service Decomposition

| Service | Responsibility | Port | Technology | Scaling |
|---------|---------------|------|------------|---------|
| **API Gateway** | Routing, auth, rate limiting | 80/443 | Kong/NGINX | Horizontal |
| **Data Service** | Ingestion, validation, preprocessing | 8001 | FastAPI + Pandas | Horizontal |
| **Training Service** | Model training, hyperparameter tuning | 8002 | FastAPI + Scikit-learn + Optuna | Vertical (GPU) |
| **Inference Service** | Prediction serving, batch/stream | 8003 | FastAPI + ONNX/TorchServe | Horizontal (3+) |
| **Evaluation Service** | Metrics, comparison, reporting | 8004 | FastAPI + MLflow | Horizontal |
| **Model Registry** | Model versioning, artifacts, metadata | 8005 | MLflow + PostgreSQL | Single (leader) |
| **Monitoring Service** | Metrics collection, alerting | 8006 | Prometheus + Grafana | Horizontal |

### Service Communication

```
┌─────────────┐     Sync (REST/gRPC)      ┌─────────────┐
│ API Gateway │◄──────────────────────────►│  Services   │
└─────────────┘                             └─────────────┘
       │                                           │
       │ Async (Message Bus)                       │ Async (Events)
       ▼                                           ▼
┌─────────────┐                             ┌─────────────┐
│   RabbitMQ  │◄────────────────────────────┤  Services   │
│   / Kafka   │   Domain Events             │  (Publish)  │
└─────────────┘                             └─────────────┘
```

### Domain Events

```python
# Example domain events
@dataclass
class DatasetLoadedEvent:
    dataset_id: str
    record_count: int
    timestamp: datetime

@dataclass
class ModelTrainedEvent:
    model_id: str
    algorithm: str
    metrics: Dict[str, float]
    artifact_path: str
    timestamp: datetime

@dataclass
class PredictionRequestedEvent:
    request_id: str
    patient_id: str
    features: Dict[str, float]
    timestamp: datetime

@dataclass
class PredictionCompletedEvent:
    request_id: str
    prediction: float
    probability: float
    model_version: str
    latency_ms: float
    timestamp: datetime
```

---

## 🔧 Technical Stack

### Current (Monolithic)
| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.11+ |
| ML Framework | Scikit-learn | 1.3+ |
| Data Processing | Pandas, NumPy | 2.0+, 1.24+ |
| Visualization | Matplotlib, Seaborn | 3.7+, 0.12+ |
| CLI | Click/Argparse | 8.1+ |
| Config | Pydantic Settings | 2.0+ |
| Testing | Pytest | 7.4+ |
| Type Checking | MyPy, Pyright | 1.5+, 1.1+ |
| Formatting | Black, isort | 23.0+, 5.12+ |

### Target (Microservices)
| Component | Technology | Justification |
|-----------|------------|---------------|
| API Framework | FastAPI | Async, auto-docs, type-safe |
| Container Runtime | Docker | Standard, portable |
| Orchestration | Kubernetes | Industry standard, auto-scaling |
| Service Mesh | Istio/Linkerd | mTLS, observability, traffic mgmt |
| Message Bus | RabbitMQ | Reliable, flexible routing |
| Model Registry | MLflow | Experiment tracking, versioning |
| Monitoring | Prometheus + Grafana | CNCF standard, powerful queries |
| Logging | ELK Stack / Loki | Centralized, searchable |
| Tracing | Jaeger | Distributed tracing |
| Config | Consul / etcd | Dynamic, distributed |
| CI/CD | GitHub Actions / ArgoCD | GitOps, native K8s |

---

## 📊 Data Architecture

### Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Raw CSV   │───►│  Validated  │───►│ Preprocessed│───►│  Features   │
│  (heart.csv)│    │   Dataset   │    │   Dataset   │    │   Store     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                                    │                    │
       │                                    ▼                    ▼
       │                            ┌─────────────┐    ┌─────────────┐
       └───────────────────────────►│  Training   │───►│   Model     │
                                    │  Pipeline   │    │  Registry   │
                                    └─────────────┘    └─────────────┘
                                                           │
                                                           ▼
                                    ┌─────────────┐    ┌─────────────┐
                                    │ Inference   │◄───│  Model      │
                                    │  Service    │    │  Artifacts  │
                                    └─────────────┘    └─────────────┘
```

### Data Models

#### Patient Record (Input)
```python
@dataclass
class PatientRecord:
    age: int                    # Age in years
    sex: int                    # 1 = male, 0 = female
    cp: int                     # Chest pain type (0-3)
    trestbps: int               # Resting blood pressure (mmHg)
    chol: int                   # Serum cholesterol (mg/dl)
    fbs: int                    # Fasting blood sugar > 120 mg/dl (1/0)
    restecg: int                # Resting ECG results (0-2)
    thalach: int                # Max heart rate achieved
    exang: int                  # Exercise induced angina (1/0)
    oldpeak: float              # ST depression induced by exercise
    slope: int                  # Slope of peak exercise ST segment (0-2)
    ca: int                     # Number of major vessels (0-3)
    thal: int                   # Thalassemia (0-3)
```

#### Prediction Output
```python
@dataclass
class PredictionResult:
    patient_id: str
    has_heart_disease: bool
    probability: float          # 0.0 - 1.0
    risk_level: Literal["low", "medium", "high"]
    model_version: str
    features_used: List[str]
    explanation: Optional[Dict]  # SHAP values (future)
    timestamp: datetime
    latency_ms: float
```

---

## 🔒 Security Architecture

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Data Injection | Input validation (Pydantic), sanitization |
| Model Poisoning | Artifact signing, integrity checks |
| Model Extraction | Rate limiting, watermarking |
| Data Leakage | Encryption at rest/transit, access controls |
| Adversarial Attacks | Input anomaly detection, robust training |

### Security Controls

- **Authentication**: JWT/OAuth2 (API Gateway)
- **Authorization**: RBAC (roles: admin, clinician, researcher)
- **Encryption**: TLS 1.3 (transit), AES-256 (rest)
- **Audit**: Structured logging, immutable audit trail
- **Compliance**: HIPAA-ready (PHI handling)

---

## 📈 Observability Architecture

### Three Pillars

```
┌─────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY                          │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   METRICS   │    LOGS     │   TRACES    │    PROFILING      │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ Prometheus  │   Loki      │   Jaeger    │   Py-Spy          │
│ Grafana     │   Grafana   │   Grafana   │   Grafana         │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ • Latency   │ • Structured│ • Request   │ • CPU/Memory      │
│ • Throughput│   JSON logs │   flow      │ • GC pauses       │
│ • Errors    │ • Correlation│ • Latency  │ • Function time   │
│ • Saturation│   IDs       │   breakdown │ • Memory leaks    │
│ • Business  │ • Levels    │ • Errors    │ • Hot paths       │
│   KPIs      │ • Sampling  │ • Spans     │                   │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

### Key Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `http_requests_total` | Counter | Total HTTP requests | - |
| `http_request_duration_seconds` | Histogram | Request latency | p99 > 500ms |
| `model_inference_duration_seconds` | Histogram | Inference latency | p99 > 100ms |
| `model_accuracy` | Gauge | Current model accuracy | < 0.80 |
| `data_drift_score` | Gauge | Feature drift detection | > 0.1 |
| `training_job_duration_seconds` | Histogram | Training time | > 600s |
| `active_models` | Gauge | Models in registry | - |

---

## 🏗️ Architecture Decision Records (ADRs)

### ADR-001: Use Clean Architecture with Feature-Based Modules
**Status**: Accepted  
**Date**: 2026-11-21  
**Context**: Need maintainable, testable architecture for ML project  
**Decision**: Adopt Clean Architecture with vertical feature slices  
**Consequences**: More initial setup, better long-term maintainability

### ADR-002: Implement MVC + Service Layer Pattern
**Status**: Accepted  
**Date**: 2026-11-21  
**Context**: Separate presentation from business logic  
**Decision**: Controllers → Services → Domain → Infrastructure  
**Consequences**: Clear separation, easier testing, swapable interfaces

### ADR-003: Design for Microservices from Start
**Status**: Accepted  
**Date**: 2026-11-21  
**Context**: Future scaling requirements  
**Decision**: Service boundaries aligned with bounded contexts  
**Consequences**: More complexity initially, smoother transition

### ADR-004: Use Pydantic for Validation and Settings
**Status**: Accepted  
**Date**: 2026-11-21  
**Context**: Need runtime validation and config management  
**Decision**: Pydantic v2 for all DTOs, settings, entities  
**Consequences**: Performance overhead, but type safety and validation

### ADR-005: MLflow for Model Registry and Experiment Tracking
**Status**: Accepted  
**Date**: 2026-11-21  
**Context**: Need model versioning, comparison, reproducibility  
**Decision**: MLflow with PostgreSQL backend and MinIO artifact store  
**Consequences**: Additional infrastructure, industry standard

---

## 🔄 Evolution Strategy

### Phase 1: Modular Monolith (Current → 3 months)
- Feature-based modules within single deployment
- Clear service boundaries internally
- Shared database, in-process communication

### Phase 2: Service Extraction (3-6 months)
- Extract Data Service first (lowest coupling)
- Extract Training Service (compute intensive)
- Shared database → separate databases per service

### Phase 3: Full Microservices (6-12 months)
- All services independently deployable
- Event-driven architecture
- Service mesh for observability/security
- GitOps deployment

---

## 📋 Quality Attributes

| Attribute | Priority | Tactics |
|-----------|----------|---------|
| **Modifiability** | High | Feature modules, DI, interfaces |
| **Testability** | High | Dependency injection, pure domain |
| **Deployability** | Medium | Containerization, config externalization |
| **Scalability** | Medium | Stateless services, horizontal scaling |
| **Availability** | Medium | Health checks, circuit breakers |
| **Security** | High | Validation, encryption, audit |
| **Performance** | Medium | Caching, async, batch processing |
| **Interoperability** | Low | REST/gRPC, OpenAPI, AsyncAPI |

---

*This document is part of Cycle 1 (SPECIFY) in the HIM-SPEC Three-Cycle Live Proof methodology.*