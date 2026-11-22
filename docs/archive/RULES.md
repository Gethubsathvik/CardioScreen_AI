# 📏 Development Rules & Standards

**Project**: Heart Disease Predictor  
**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-11-21  
**Cycle**: 1 - SPECIFY (HIM-SPEC Three-Cycle Live Proof)

---

## 🎯 Purpose

This document establishes **mandatory** development rules, coding standards, and practices for the Heart Disease Predictor project. All contributors **must** follow these rules without exception.

---

## 🐍 Python Code Standards

### Version & Environment
- **Python Version**: 3.11+ (minimum 3.10)
- **Virtual Environment**: Required for all development
- **Dependency Management**: `pip` + `requirements.txt` + `requirements-dev.txt`
- **Lock Files**: `pip-tools` for deterministic builds

### Type Hints (MANDATORY)
```python
# ✅ GOOD: Full type hints
def predict_heart_disease(
    features: PatientFeatures,
    model: BaseEstimator,
    threshold: float = 0.5
) -> PredictionResult:
    ...

# ❌ BAD: Missing type hints
def predict(features, model, threshold=0.5):
    ...
```

**Rules**:
- All function signatures **must** have type hints
- Use `from __future__ import annotations` for forward references
- No `Any` type without justification (add `# type: ignore[...]` comment)
- Generic types: `List[T]`, `Dict[K, V]`, `Optional[T]`, `Union[A, B]`
- Protocol classes for duck typing interfaces

### Code Formatting (MANDATORY)
```bash
# Run before every commit
black --line-length=100 src/ tests/
isort --profile=black --line-length=100 src/ tests/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### Linting (MANDATORY)
```bash
# Run before every commit
flake8 src/ tests/
mypy --strict src/
pyright src/
```

**Configuration**:
```toml
# pyproject.toml
[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
exclude = [".git", "__pycache__", ".venv", "venv", "build", "dist"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
```

### Import Organization
```python
# 1. Standard library
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# 2. Third-party
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

# 3. Local application (absolute imports)
from src.shared.config import settings
from src.shared.exceptions import ValidationError
from src.features.data_ingestion.domain.entities import Dataset

# 4. Relative imports (within same feature only)
from .domain.value_objects import ColumnSchema
```

---

## 📝 Documentation Standards

### Docstrings (Google Style - MANDATORY)
```python
def train_model(
    X: np.ndarray,
    y: np.ndarray,
    algorithm: str = "logistic_regression",
    hyperparameters: Optional[Dict[str, Any]] = None,
) -> Tuple[BaseEstimator, Dict[str, float]]:
    """Train a machine learning model for heart disease prediction.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Target vector of shape (n_samples,).
        algorithm: Name of the algorithm to use. Defaults to "logistic_regression".
        hyperparameters: Optional dictionary of algorithm-specific hyperparameters.

    Returns:
        A tuple of (trained_model, training_metrics) where training_metrics
        contains accuracy, precision, recall, and f1_score.

    Raises:
        ValueError: If algorithm is not supported or data is invalid.
        TrainingError: If model training fails.

    Example:
        >>> X, y = load_data()
        >>> model, metrics = train_model(X, y, "random_forest")
        >>> print(f"Accuracy: {metrics['accuracy']:.4f}")
    """
```

### Module Documentation
```python
"""Data Ingestion Feature Module.

This module handles loading, validation, and preprocessing of heart disease datasets.
It provides a clean interface for data pipeline operations.

Components:
    - Domain: Core entities, value objects, and domain services
    - Application: Use cases and application services
    - Infrastructure: External adapters and repositories
    - Interfaces: CLI commands and API routes

Example:
    >>> from src.features.data_ingestion.application.use_cases import LoadDatasetUseCase
    >>> use_case = LoadDatasetUseCase(csv_repository)
    >>> dataset = use_case.execute("data/heart.csv")
"""
```

---

## 🏗️ Architecture Rules

### Layer Dependencies (STRICT)
```
┌─────────────────────────────────────┐
│         PRESENTATION (CLI/API)      │  ◄── Can import from Controller, Service
├─────────────────────────────────────┤
│           CONTROLLER LAYER          │  ◄── Can import from Service, Domain
├─────────────────────────────────────┤
│            SERVICE LAYER            │  ◄── Can import from Domain, Shared
├─────────────────────────────────────┤
│             DOMAIN LAYER            │  ◄── Can import from Shared ONLY
├─────────────────────────────────────┤
│            SHARED KERNEL            │  ◄── No internal dependencies
├─────────────────────────────────────┤
│         INFRASTRUCTURE LAYER        │  ◄── Implements Domain interfaces
└─────────────────────────────────────┘
```

**FORBIDDEN**:
- Domain importing from Infrastructure
- Service importing from Presentation
- Controller importing from Infrastructure directly
- Circular dependencies between features

### Dependency Injection (MANDATORY)
```python
# ✅ GOOD: Constructor injection
class TrainingService:
    def __init__(
        self,
        model_repository: ModelRepository,
        experiment_tracker: ExperimentTracker,
    ):
        self._model_repo = model_repository
        self._tracker = experiment_tracker

# ❌ BAD: Direct instantiation
class TrainingService:
    def __init__(self):
        self._model_repo = MLflowModelRepository()  # Hardcoded dependency
```

### Interface Segregation
```python
# ✅ GOOD: Small, focused protocols
class ModelRepository(Protocol):
    def save(self, model: BaseEstimator, metadata: ModelMetadata) -> str: ...
    def load(self, model_id: str) -> BaseEstimator: ...
    def delete(self, model_id: str) -> bool: ...

class ExperimentTracker(Protocol):
    def log_params(self, params: Dict[str, Any]) -> None: ...
    def log_metrics(self, metrics: Dict[str, float]) -> None: ...
    def log_artifact(self, path: Path) -> None: ...

# ❌ BAD: Fat interface
class MLService(Protocol):
    def save_model(self, ...): ...
    def load_model(self, ...): ...
    def track_experiment(self, ...): ...
    def log_params(self, ...): ...
    def log_metrics(self, ...): ...
    def log_artifact(self, ...): ...
```

---

## 🧪 Testing Standards

### Test Organization
```
tests/
├── unit/                       # Fast, isolated tests (< 100ms each)
│   ├── test_shared/
│   ├── test_features/
│   │   ├── test_data_ingestion/
│   │   ├── test_model_training/
│   │   ├── test_model_evaluation/
│   │   └── test_prediction/
├── integration/                # Service/database tests (< 5s each)
│   ├── test_training_pipeline.py
│   └── test_prediction_pipeline.py
├── e2e/                        # Full workflow tests (< 30s each)
│   └── test_full_workflow.py
├── contract/                   # API contract tests
└── fixtures/                   # Test data and helpers
```

### Test Naming
```python
# ✅ GOOD: Descriptive names
def test_train_model_returns_fitted_estimator_and_metrics():
    ...

def test_predict_raises_validation_error_for_invalid_features():
    ...

def test_data_validator_rejects_missing_required_columns():
    ...

# ❌ BAD: Vague names
def test_train():
    ...

def test_predict_error():
    ...
```

### Test Structure (AAA Pattern)
```python
def test_predict_returns_correct_probability_for_known_patient():
    # ARRANGE
    model = create_mock_model(probability=0.85)
    features = create_valid_patient_features()
    
    # ACT
    result = predictor.predict(features)
    
    # ASSERT
    assert result.has_heart_disease is True
    assert result.probability == 0.85
    assert result.risk_level == "high"
```

### Coverage Requirements
| Metric | Minimum |
|--------|---------|
| Line Coverage | 80% |
| Branch Coverage | 75% |
| Function Coverage | 85% |
| Critical Paths | 100% |

### Test Fixtures
```python
# conftest.py
import pytest
import numpy as np
from src.shared.types import PatientFeatures

@pytest.fixture
def sample_patient() -> PatientFeatures:
    return PatientFeatures(
        age=63, sex=1, cp=3, trestbps=145, chol=233,
        fbs=1, restecg=0, thalach=150, exang=0,
        oldpeak=2.3, slope=0, ca=0, thal=1
    )

@pytest.fixture
def trained_model(sample_dataset) -> LogisticRegression:
    model = LogisticRegression(random_state=42)
    model.fit(sample_dataset.X, sample_dataset.y)
    return model
```

---

## 🔄 Git & Version Control

### Branching Strategy
```
main (protected)
  ├── develop (integration branch)
  │   ├── feature/US-XXX-description
  │   ├── bugfix/ISSUE-XXX-description
  │   └── hotfix/CRITICAL-XXX-description
  └── release/vX.Y.Z
```

### Commit Messages (Conventional Commits - MANDATORY)
```bash
# Format: <type>(<scope>): <subject>
# Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build

# ✅ GOOD
feat(data_ingestion): add CSV schema validation
fix(model_training): handle NaN values in preprocessing
docs(architecture): update microservices diagram
refactor(shared): extract base repository interface
test(prediction): add edge case tests for invalid input

# ❌ BAD
fixed bug
updated code
wip
```

### Pull Request Requirements
- [ ] All CI checks pass (lint, type-check, tests)
- [ ] Code coverage maintained (> 80%)
- [ ] Documentation updated for public APIs
- [ ] CHANGELOG.md updated (for feat/fix)
- [ ] At least 1 approval from team member
- [ ] No merge conflicts with target branch

---

## 🔐 Security Rules

### Input Validation (MANDATORY)
```python
# ✅ GOOD: Pydantic validation
class PatientFeatures(BaseModel):
    age: int = Field(ge=0, le=120, description="Age in years")
    sex: Literal[0, 1] = Field(description="0=female, 1=male")
    cp: Literal[0, 1, 2, 3] = Field(description="Chest pain type")
    # ... all fields validated

# Usage
def predict(features: PatientFeatures) -> PredictionResult:
    validated = PatientFeatures.model_validate(features)  # Raises ValidationError
    ...
```

### Secrets Management
- **NEVER** commit secrets (API keys, passwords, tokens)
- Use `.env` files (gitignored) for local development
- Use environment variables in production
- Use secret managers (AWS Secrets Manager, HashiCorp Vault) in K8s

```bash
# .env.example (commit this)
DATABASE_URL=postgresql://user:pass@localhost:5432/heartdb
MLFLOW_TRACKING_URI=http://localhost:5000
SECRET_KEY=your-secret-key-here

# .env (DO NOT COMMIT)
DATABASE_URL=postgresql://prod:realpass@db:5432/heartdb
SECRET_KEY=actual-production-secret
```

### Dependency Security
```bash
# Run regularly
pip-audit                    # Check for vulnerabilities
safety check                 # Alternative checker
pip list --outdated          # Check for updates
```

---

## 📦 Dependency Management

### Requirements Files
```
requirements.txt              # Production dependencies (pinned)
requirements-dev.txt          # Development dependencies
requirements-test.txt         # Test-only dependencies
requirements-docs.txt         # Documentation dependencies
```

### Pinning Strategy
```txt
# requirements.txt
# Core ML
scikit-learn==1.3.2
numpy==1.26.0
pandas==2.1.3
scipy==1.11.3

# Visualization
matplotlib==3.8.0
seaborn==0.13.0

# API/Config
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Utilities
joblib==1.3.2
tqdm==4.66.1
```

### Adding Dependencies
1. Add to appropriate `requirements-*.txt`
2. Run `pip-compile` to update lock files
3. Update `pyproject.toml` if build dependency
4. Document why in PR description

---

## 🚀 CI/CD Rules

### Pipeline Stages (Required Order)
```yaml
# .github/workflows/ci.yml
stages:
  1. lint          # flake8, black --check, isort --check
  2. typecheck     # mypy, pyright
  3. test-unit     # pytest tests/unit -x --cov
  4. test-integration # pytest tests/integration
  5. test-contract  # pact/schematic tests
  6. build         # docker build
  7. scan          # trivy, pip-audit
  8. deploy-staging # on develop branch
  9. deploy-prod    # on main branch (manual approval)
```

### Quality Gates (Blocking)
| Check | Threshold | Action on Fail |
|-------|-----------|----------------|
| Linting | 0 errors | Block merge |
| Type Checking | 0 errors | Block merge |
| Unit Tests | 100% pass | Block merge |
| Coverage | ≥ 80% lines | Block merge |
| Security Scan | 0 critical/high | Block merge |
| Docker Build | Success | Block merge |

---

## 📊 Performance Rules

### Profiling Requirements
```python
# Add to critical paths
import cProfile
import pstats

def profile_training():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # ... training code ...
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(20)
```

### Benchmarks
- Training time: < 10 minutes (full dataset)
- Inference latency: < 50ms p99
- Memory usage: < 2GB (training), < 500MB (inference)
- Batch prediction (1000): < 5 seconds

---

## 📝 Changelog Rules

### Format (Keep a Changelog)
```markdown
# Changelog

## [1.2.0] - 2026-11-21
### Added
- Multi-algorithm support (SVM, Random Forest, KNN)
- Hyperparameter tuning with Optuna
- ROC curve visualization

### Changed
- Refactored to feature-based architecture
- Updated to Pydantic v2

### Fixed
- Memory leak in batch prediction
- Data validation for edge cases

### Removed
- Deprecated CLI commands
```

### Versioning (SemVer)
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

---

## 🎯 Definition of Done

A task is **DONE** only when:
- [ ] Code implemented per requirements
- [ ] Unit tests written and passing (> 80% coverage)
- [ ] Integration tests passing (if applicable)
- [ ] Linting passes (flake8, black, isort)
- [ ] Type checking passes (mypy strict, pyright)
- [ ] Documentation updated (docstrings, module docs, README)
- [ ] Code reviewed and approved
- [ ] Merged to target branch
- [ ] Deployed to staging (for features)
- [ ] Verified in staging environment

---

## 🚫 Anti-Patterns (FORBIDDEN)

| Anti-Pattern | Why | Alternative |
|--------------|-----|-------------|
| God classes | Violates SRP | Split into focused services |
| Circular imports | Breaks architecture | Dependency inversion |
| Mutable global state | Hard to test, debug | Dependency injection |
| Catch-all exceptions | Hides bugs | Specific exception handling |
| Magic numbers/strings | Unmaintainable | Constants/enums |
| Copy-paste code | Duplication | Shared utilities, inheritance |
| Premature optimization | Complexity without need | Profile first, optimize after |
| Comments explaining "what" | Code should be self-documenting | Clear naming, type hints |
| Large functions (> 50 lines) | Hard to understand, test | Extract to smaller functions |

---

## 🔧 Tool Configuration

### EditorConfig (`.editorconfig`)
```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{py,pyi}]
indent_size = 4

[*.{yml,yaml,json,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### Pre-commit (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [pydantic, numpy, pandas, scikit-learn]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
```

---

*This document is part of Cycle 1 (SPECIFY) in the HIM-SPEC Three-Cycle Live Proof methodology. All rules are **mandatory** and enforced via CI/CD.*