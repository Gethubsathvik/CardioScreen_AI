# 📐 Design Specifications

**Project**: Heart Disease Predictor  
**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-11-21  
**Cycle**: 1 - SPECIFY (HIM-SPEC Three-Cycle Live Proof)

---

## 🎯 Design Overview

This document provides detailed design specifications for the Heart Disease Predictor system, including data models, API contracts, algorithm implementations, UI/UX designs, and integration patterns.

---

## 📊 Data Models

### 1. Patient Features (Input Schema)

```python
# src/shared/schemas/patient.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import IntEnum

class Sex(IntEnum):
    FEMALE = 0
    MALE = 1

class ChestPainType(IntEnum):
    TYPICAL_ANGINA = 0
    ATYPICAL_ANGINA = 1
    NON_ANGINAL_PAIN = 2
    ASYMPTOMATIC = 3

class RestingECG(IntEnum):
    NORMAL = 0
    ST_T_WAVE_ABNORMALITY = 1
    LEFT_VENTRICULAR_HYPERTROPHY = 2

class ExerciseAngina(IntEnum):
    NO = 0
    YES = 1

class ST_Slope(IntEnum):
    UPSLOPING = 0
    FLAT = 1
    DOWNSLOPING = 2

class Thalassemia(IntEnum):
    NORMAL = 0
    FIXED_DEFECT = 1
    REVERSIBLE_DEFECT = 2
    UNKNOWN = 3

class PatientFeatures(BaseModel):
    """Clinical features for heart disease prediction.
    
    Based on UCI Heart Disease dataset attributes.
    """
    age: int = Field(
        ge=1, le=120,
        description="Age in years",
        examples=[63]
    )
    sex: Sex = Field(
        description="Sex of the patient",
        examples=[Sex.MALE]
    )
    cp: ChestPainType = Field(
        description="Chest pain type",
        examples=[ChestPainType.ASYMPTOMATIC]
    )
    trestbps: int = Field(
        ge=50, le=250,
        description="Resting blood pressure (mmHg)",
        examples=[145]
    )
    chol: int = Field(
        ge=50, le=600,
        description="Serum cholesterol (mg/dl)",
        examples=[233]
    )
    fbs: Literal[0, 1] = Field(
        description="Fasting blood sugar > 120 mg/dl",
        examples=[1]
    )
    restecg: RestingECG = Field(
        description="Resting electrocardiographic results",
        examples=[RestingECG.NORMAL]
    )
    thalach: int = Field(
        ge=50, le=250,
        description="Maximum heart rate achieved",
        examples=[150]
    )
    exang: ExerciseAngina = Field(
        description="Exercise induced angina",
        examples=[ExerciseAngina.NO]
    )
    oldpeak: float = Field(
        ge=0.0, le=10.0,
        description="ST depression induced by exercise relative to rest",
        examples=[2.3]
    )
    slope: ST_Slope = Field(
        description="Slope of the peak exercise ST segment",
        examples=[ST_Slope.FLAT]
    )
    ca: Literal[0, 1, 2, 3] = Field(
        description="Number of major vessels colored by fluoroscopy",
        examples=[0]
    )
    thal: Thalassemia = Field(
        description="Thalassemia type",
        examples=[Thalassemia.NORMAL]
    )

    @field_validator('age', 'trestbps', 'chol', 'thalach')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Must be positive')
        return v

    def to_array(self) -> list:
        """Convert to feature array for model input."""
        return [
            self.age, self.sex, self.cp, self.trestbps, self.chol,
            self.fbs, self.restecg, self.thalach, self.exang,
            self.oldpeak, self.slope, self.ca, self.thal
        ]

    def to_dataframe(self) -> "pd.DataFrame":
        """Convert to pandas DataFrame for batch processing."""
        import pandas as pd
        return pd.DataFrame([self.model_dump()])
```

### 2. Prediction Result (Output Schema)

```python
# src/shared/schemas/prediction.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PredictionResult(BaseModel):
    """Heart disease prediction result."""
    patient_id: str = Field(description="Unique patient identifier")
    has_heart_disease: bool = Field(description="Binary prediction result")
    probability: float = Field(
        ge=0.0, le=1.0,
        description="Probability of heart disease (0-1)"
    )
    risk_level: RiskLevel = Field(description="Categorical risk level")
    model_version: str = Field(description="Model version used for prediction")
    model_algorithm: str = Field(description="Algorithm name")
    features_used: List[str] = Field(description="List of feature names used")
    explanation: Optional[Dict[str, float]] = Field(
        default=None,
        description="SHAP values or feature contributions (future)"
    )
    confidence_interval: Optional[tuple[float, float]] = Field(
        default=None,
        description="95% confidence interval for probability"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: float = Field(description="Inference latency in milliseconds")

    @property
    def risk_score(self) -> int:
        """Integer risk score 0-100."""
        return int(self.probability * 100)

    def to_clinical_report(self) -> str:
        """Generate human-readable clinical report."""
        return f"""
Heart Disease Risk Assessment
=============================
Patient ID: {self.patient_id}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Prediction: {"Positive" if self.has_heart_disease else "Negative"}
Probability: {self.probability:.2%}
Risk Level: {self.risk_level.value.upper()}
Risk Score: {self.risk_score}/100

Model: {self.model_algorithm} v{self.model_version}
Features: {', '.join(self.features_used)}
Latency: {self.latency_ms:.1f}ms

Disclaimer: This is a screening tool, not a diagnostic tool.
Clinical correlation required.
"""
```

### 3. Training Metrics Schema

```python
# src/shared/schemas/training.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class TrainingMetrics(BaseModel):
    """Model training evaluation metrics."""
    algorithm: str = Field(description="Algorithm name")
    model_version: str = Field(description="Generated model version")
    
    # Primary metrics
    accuracy: float = Field(ge=0.0, le=1.0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1_score: float = Field(ge=0.0, le=1.0)
    roc_auc: float = Field(ge=0.0, le=1.0)
    
    # Per-class metrics
    precision_per_class: Dict[str, float] = Field(default_factory=dict)
    recall_per_class: Dict[str, float] = Field(default_factory=dict)
    f1_per_class: Dict[str, float] = Field(default_factory=dict)
    
    # Cross-validation
    cv_scores: List[float] = Field(default_factory=list)
    cv_mean: Optional[float] = None
    cv_std: Optional[float] = None
    
    # Training info
    training_time_seconds: float = Field(description="Training duration")
    n_samples: int = Field(description="Training sample count")
    n_features: int = Field(description="Feature count")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Data splits
    train_size: int
    test_size: int
    validation_size: Optional[int] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_comparison_dict(self) -> Dict[str, float]:
        """Extract metrics for model comparison."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "roc_auc": self.roc_auc,
            "cv_mean": self.cv_mean or 0.0,
        }
```

---

## 🔌 API Design

### REST API Specification (OpenAPI 3.0)

```yaml
# docs/api/openapi.yaml
openapi: 3.0.3
info:
  title: Heart Disease Predictor API
  version: 1.0.0
  description: REST API for heart disease prediction and model management
  contact:
    name: API Support
    email: api@heartpredictor.example.com
servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.heartpredictor.example.com/v1
    description: Production server

paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

  /predict:
    post:
      summary: Single patient prediction
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PredictionRequest'
      responses:
        '200':
          description: Successful prediction
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PredictionResponse'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '422':
          description: Validation error
        '500':
          description: Internal server error

  /predict/batch:
    post:
      summary: Batch prediction
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BatchPredictionRequest'
      responses:
        '200':
          description: Batch predictions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchPredictionResponse'
        '400':
          description: Invalid input
        '413':
          description: Payload too large (max 1000 records)

  /models:
    get:
      summary: List available models
      parameters:
        - name: algorithm
          in: query
          schema:
            type: string
            enum: [logistic_regression, svm, random_forest, knn, kmeans, decision_tree]
      responses:
        '200':
          description: List of models
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModelListResponse'

  /models/{model_id}:
    get:
      summary: Get model details
      parameters:
        - name: model_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Model details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModelDetailResponse'
        '404':
          description: Model not found

  /models/{model_id}/metrics:
    get:
      summary: Get model performance metrics
      parameters:
        - name: model_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Model metrics
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TrainingMetrics'

  /train:
    post:
      summary: Trigger model training
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TrainingRequest'
      responses:
        '202':
          description: Training job started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TrainingJobResponse'
        '400':
          description: Invalid training configuration

  /train/{job_id}:
    get:
      summary: Get training job status
      parameters:
        - name: job_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Job status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TrainingJobStatus'

components:
  schemas:
    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        version:
          type: string
        timestamp:
          type: string
          format: date-time
        checks:
          type: object
          additionalProperties:
            type: boolean

    PredictionRequest:
      type: object
      required: [patient_id, features]
      properties:
        patient_id:
          type: string
          format: uuid
        features:
          $ref: '#/components/schemas/PatientFeatures'
        model_id:
          type: string
          description: Optional specific model version
        return_explanation:
          type: boolean
          default: false

    PatientFeatures:
      type: object
      required: [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
      properties:
        age:
          type: integer
          minimum: 1
          maximum: 120
        sex:
          type: integer
          enum: [0, 1]
        cp:
          type: integer
          enum: [0, 1, 2, 3]
        trestbps:
          type: integer
          minimum: 50
          maximum: 250
        chol:
          type: integer
          minimum: 50
          maximum: 600
        fbs:
          type: integer
          enum: [0, 1]
        restecg:
          type: integer
          enum: [0, 1, 2]
        thalach:
          type: integer
          minimum: 50
          maximum: 250
        exang:
          type: integer
          enum: [0, 1]
        oldpeak:
          type: number
          minimum: 0
          maximum: 10
        slope:
          type: integer
          enum: [0, 1, 2]
        ca:
          type: integer
          enum: [0, 1, 2, 3]
        thal:
          type: integer
          enum: [0, 1, 2, 3]

    PredictionResponse:
      type: object
      properties:
        patient_id:
          type: string
        has_heart_disease:
          type: boolean
        probability:
          type: number
          minimum: 0
          maximum: 1
        risk_level:
          type: string
          enum: [low, medium, high]
        model_version:
          type: string
        model_algorithm:
          type: string
        features_used:
          type: array
          items:
            type: string
        explanation:
          type: object
          additionalProperties:
            type: number
        confidence_interval:
          type: array
          items:
            type: number
          minItems: 2
          maxItems: 2
        timestamp:
          type: string
          format: date-time
        latency_ms:
          type: number

    BatchPredictionRequest:
      type: object
      required: [predictions]
      properties:
        predictions:
          type: array
          items:
            $ref: '#/components/schemas/PredictionRequest'
          minItems: 1
          maxItems: 1000

    BatchPredictionResponse:
      type: object
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/PredictionResponse'
        summary:
          type: object
          properties:
            total:
              type: integer
            positive:
              type: integer
            negative:
              type: integer
            avg_latency_ms:
              type: number

    ModelListResponse:
      type: object
      properties:
        models:
          type: array
          items:
            $ref: '#/components/schemas/ModelSummary'
        total:
          type: integer

    ModelSummary:
      type: object
      properties:
        model_id:
          type: string
        algorithm:
          type: string
        version:
          type: string
        accuracy:
          type: number
        roc_auc:
          type: number
        created_at:
          type: string
          format: date-time
        is_active:
          type: boolean

    ModelDetailResponse:
      type: object
      properties:
        model_id:
          type: string
        algorithm:
          type: string
        version:
          type: string
        hyperparameters:
          type: object
        metrics:
          $ref: '#/components/schemas/TrainingMetrics'
        feature_importance:
          type: object
          additionalProperties:
            type: number
        created_at:
          type: string
          format: date-time
        artifact_path:
          type: string

    TrainingRequest:
      type: object
      required: [algorithm]
      properties:
        algorithm:
          type: string
          enum: [logistic_regression, svm, random_forest, knn, kmeans, decision_tree]
        hyperparameters:
          type: object
        cv_folds:
          type: integer
          default: 5
          minimum: 2
          maximum: 10
        test_size:
          type: number
          default: 0.2
          minimum: 0.1
          maximum: 0.5
        random_state:
          type: integer
          default: 42
        tune_hyperparameters:
          type: boolean
          default: false
        tuning_trials:
          type: integer
          default: 50
          minimum: 10
          maximum: 200

    TrainingJobResponse:
      type: object
      properties:
        job_id:
          type: string
        status:
          type: string
          enum: [pending, running, completed, failed]
        message:
          type: string

    TrainingJobStatus:
      type: object
      properties:
        job_id:
          type: string
        status:
          type: string
          enum: [pending, running, completed, failed]
        progress:
          type: number
          minimum: 0
          maximum: 100
        current_step:
          type: string
        metrics:
          $ref: '#/components/schemas/TrainingMetrics'
        error:
          type: string
        started_at:
          type: string
          format: date-time
        completed_at:
          type: string
          format: date-time

    TrainingMetrics:
      type: object
      properties:
        algorithm:
          type: string
        model_version:
          type: string
        accuracy:
          type: number
        precision:
          type: number
        recall:
          type: number
        f1_score:
          type: number
        roc_auc:
          type: number
        cv_scores:
          type: array
          items:
            type: number
        cv_mean:
          type: number
        cv_std:
          type: number
        training_time_seconds:
          type: number
        n_samples:
          type: integer
        n_features:
          type: integer
        hyperparameters:
          type: object
        timestamp:
          type: string
          format: date-time

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: object
        timestamp:
          type: string
          format: date-time
        request_id:
          type: string
```

---

## 🧠 Algorithm Design

### Base Algorithm Interface

```python
# src/features/model_training/domain/algorithms/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.base import BaseEstimator

class AlgorithmConfig(BaseModel):
    """Base configuration for all algorithms."""
    random_state: int = 42
    n_jobs: int = -1
    verbose: int = 0

class BaseAlgorithm(ABC):
    """Abstract base class for all ML algorithms."""
    
    # Class attributes
    name: str = "base"
    display_name: str = "Base Algorithm"
    supports_probability: bool = True
    supports_multiclass: bool = True
    default_params: Dict[str, Any] = {}
    param_grid: Dict[str, List[Any]] = {}
    
    def __init__(self, config: Optional[AlgorithmConfig] = None, **params):
        self.config = config or AlgorithmConfig()
        self.params = {**self.default_params, **params}
        self.model: Optional[BaseEstimator] = None
        self.is_fitted: bool = False
        self.feature_names: List[str] = []
        self.training_metrics: Dict[str, float] = {}
    
    @abstractmethod
    def _create_model(self) -> BaseEstimator:
        """Create the underlying sklearn estimator."""
        pass
    
    @abstractmethod
    def get_param_grid(self) -> Dict[str, List[Any]]:
        """Return hyperparameter grid for tuning."""
        pass
    
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        sample_weight: Optional[np.ndarray] = None,
    ) -> "BaseAlgorithm":
        """Train the model."""
        self.model = self._create_model()
        self.model.set_params(**self.params)
        
        if sample_weight is not None:
            self.model.fit(X, y, sample_weight=sample_weight)
        else:
            self.model.fit(X, y)
        
        self.is_fitted = True
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        if not self.supports_probability:
            raise NotImplementedError("Algorithm does not support probability predictions")
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = np.abs(self.model.coef_).mean(axis=0)
        else:
            return {}
        
        return dict(zip(self.feature_names, importances.tolist()))
    
    def get_params(self) -> Dict[str, Any]:
        """Get current parameters."""
        return {**self.params, **self.config.model_dump()}
    
    def set_params(self, **params) -> "BaseAlgorithm":
        """Set parameters."""
        self.params.update(params)
        if self.model is not None:
            self.model.set_params(**params)
        return self
```

### Algorithm Implementations

#### 1. Logistic Regression
```python
# src/features/model_training/domain/algorithms/logistic_regression.py
from sklearn.linear_model import LogisticRegression
import numpy as np
from typing import Dict, List, Any
from .base import BaseAlgorithm, AlgorithmConfig

class LogisticRegressionAlgorithm(BaseAlgorithm):
    name = "logistic_regression"
    display_name = "Logistic Regression"
    supports_probability = True
    
    default_params = {
        "penalty": "l2",
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "class_weight": "balanced",
    }
    
    param_grid = {
        "C": [0.01, 0.1, 1.0, 10.0, 100.0],
        "penalty": ["l1", "l2", "elasticnet"],
        "solver": ["lbfgs", "liblinear", "saga"],
        "max_iter": [500, 1000, 2000],
    }
    
    def _create_model(self) -> LogisticRegression:
        return LogisticRegression(random_state=self.config.random_state)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
```

#### 2. Support Vector Machine
```python
# src/features/model_training/domain/algorithms/svm.py
from sklearn.svm import SVC
from typing import Dict, List, Any
from .base import BaseAlgorithm, AlgorithmConfig

class SVMAlgorithm(BaseAlgorithm):
    name = "svm"
    display_name = "Support Vector Machine"
    supports_probability = True
    
    default_params = {
        "kernel": "rbf",
        "C": 1.0,
        "gamma": "scale",
        "probability": True,
        "class_weight": "balanced",
    }
    
    param_grid = {
        "C": [0.1, 1.0, 10.0, 100.0],
        "kernel": ["rbf", "linear", "poly", "sigmoid"],
        "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1.0],
        "degree": [2, 3, 4],  # for poly kernel
    }
    
    def _create_model(self) -> SVC:
        return SVC(random_state=self.config.random_state)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
```

#### 3. Random Forest
```python
# src/features/model_training/domain/algorithms/random_forest.py
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, List, Any
from .base import BaseAlgorithm, AlgorithmConfig

class RandomForestAlgorithm(BaseAlgorithm):
    name = "random_forest"
    display_name = "Random Forest"
    supports_probability = True
    
    default_params = {
        "n_estimators": 100,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "class_weight": "balanced",
    }
    
    param_grid = {
        "n_estimators": [50, 100, 200, 500],
        "max_depth": [None, 5, 10, 15, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
    }
    
    def _create_model(self) -> RandomForestClassifier:
        return RandomForestClassifier(random_state=self.config.random_state, n_jobs=self.config.n_jobs)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
```

#### 4. K-Nearest Neighbors
```python
# src/features/model_training/domain/algorithms/knn.py
from sklearn.neighbors import KNeighborsClassifier
from typing import Dict, List, Any
from .base import BaseAlgorithm, AlgorithmConfig

class KNNAlgorithm(BaseAlgorithm):
    name = "knn"
    display_name = "K-Nearest Neighbors"
    supports_probability = True
    
    default_params = {
        "n_neighbors": 5,
        "weights": "uniform",
        "metric": "minkowski",
        "p": 2,
    }
    
    param_grid = {
        "n_neighbors": [3, 5, 7, 9, 11, 15],
        "weights": ["uniform", "distance"],
        "metric": ["euclidean", "manhattan", "minkowski", "chebyshev"],
        "p": [1, 2, 3],
    }
    
    def _create_model(self) -> KNeighborsClassifier:
        return KNeighborsClassifier(n_jobs=self.config.n_jobs)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
```

#### 5. K-Means Clustering
```python
# src/features/model_training/domain/algorithms/kmeans.py
from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator
from typing import Dict, List, Any
import numpy as np
from .base import BaseAlgorithm, AlgorithmConfig

class KMeansAlgorithm(BaseAlgorithm):
    name = "kmeans"
    display_name = "K-Means Clustering"
    supports_probability = False
    supports_multiclass = False  # Unsupervised
    
    default_params = {
        "n_clusters": 2,
        "init": "k-means++",
        "n_init": 10,
        "max_iter": 300,
    }
    
    param_grid = {
        "n_clusters": [2, 3, 4, 5],
        "init": ["k-means++", "random"],
        "n_init": [5, 10, 20],
        "max_iter": [100, 300, 500],
    }
    
    def _create_model(self) -> KMeans:
        return KMeans(random_state=self.config.random_state)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
    
    def fit(self, X: np.ndarray, y: np.ndarray = None, **kwargs) -> "KMeansAlgorithm":
        """K-Means is unsupervised - ignores y."""
        self.model = self._create_model()
        self.model.set_params(**self.params)
        self.model.fit(X)
        self.is_fitted = True
        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster labels."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return distance to cluster centers as pseudo-probabilities."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        distances = self.model.transform(X)
        # Convert distances to probabilities (inverse distance)
        with np.errstate(divide='ignore', invalid='ignore'):
            probs = 1 / (distances + 1e-10)
            probs = probs / probs.sum(axis=1, keepdims=True)
        return probs
```

#### 6. Decision Tree
```python
# src/features/model_training/domain/algorithms/decision_tree.py
from sklearn.tree import DecisionTreeClassifier
from typing import Dict, List, Any
from .base import BaseAlgorithm, AlgorithmConfig

class DecisionTreeAlgorithm(BaseAlgorithm):
    name = "decision_tree"
    display_name = "Decision Tree"
    supports_probability = True
    
    default_params = {
        "criterion": "gini",
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "max_features": None,
        "class_weight": "balanced",
    }
    
    param_grid = {
        "criterion": ["gini", "entropy", "log_loss"],
        "max_depth": [None, 3, 5, 7, 10, 15],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [1, 2, 4, 8],
        "max_features": [None, "sqrt", "log2"],
    }
    
    def _create_model(self) -> DecisionTreeClassifier:
        return DecisionTreeClassifier(random_state=self.config.random_state)
    
    def get_param_grid(self) -> Dict[str, List[Any]]:
        return self.param_grid
```

---

## 🎨 Visualization Design

### Plot Specifications

```python
# src/features/model_evaluation/domain/visualization/plots.py
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class PlotStyle:
    """Consistent styling for all visualizations."""
    
    # Color palette
    COLORS = {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "success": "#28A745",
        "warning": "#FFC107",
        "danger": "#DC3545",
        "info": "#17A2B8",
        "light": "#F8F9FA",
        "dark": "#343A40",
    }
    
    # Color sequences
    PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E", "#BC4B51"]
    PALETTE_DIVERGING = ["#2E86AB", "#F8F9FA", "#A23B72"]
    
    # Figure settings
    FIGSIZE_SMALL = (8, 6)
    FIGSIZE_MEDIUM = (10, 8)
    FIGSIZE_LARGE = (12, 10)
    FIGSIZE_WIDE = (14, 6)
    
    # Font sizes
    TITLE_SIZE = 16
    LABEL_SIZE = 12
    TICK_SIZE = 10
    LEGEND_SIZE = 10
    ANNOTATION_SIZE = 9
    
    @classmethod
    def apply_style(cls):
        """Apply consistent matplotlib style."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.figsize': cls.FIGSIZE_MEDIUM,
            'font.size': cls.LABEL_SIZE,
            'axes.titlesize': cls.TITLE_SIZE,
            'axes.labelsize': cls.LABEL_SIZE,
            'xtick.labelsize': cls.TICK_SIZE,
            'ytick.labelsize': cls.TICK_SIZE,
            'legend.fontsize': cls.LEGEND_SIZE,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.edgecolor': '#CCCCCC',
            'grid.color': '#E0E0E0',
            'grid.linewidth': 0.5,
        })
        sns.set_palette(cls.PALETTE)


def plot_roc_curve(
    fpr: np.ndarray,
    tpr: np.ndarray,
    auc_score: float,
    model_name: str = "Model",
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot ROC curve with AUC score."""
    PlotStyle.apply_style()
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_MEDIUM)
    
    # ROC curve
    ax.plot(
        fpr, tpr,
        color=PlotStyle.COLORS["primary"],
        lw=2.5,
        label=f'{model_name} (AUC = {auc_score:.3f})'
    )
    
    # Diagonal line
    ax.plot(
        [0, 1], [0, 1],
        color=PlotStyle.COLORS["dark"],
        lw=1.5,
        linestyle='--',
        alpha=0.7,
        label='Random Classifier (AUC = 0.50)'
    )
    
    # Fill area under curve
    ax.fill_between(
        fpr, tpr,
        alpha=0.15,
        color=PlotStyle.COLORS["primary"]
    )
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontweight='bold')
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontweight='bold')
    ax.set_title(f'ROC Curve - {model_name}', fontweight='bold', pad=15)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Add AUC annotation
    ax.annotate(
        f'AUC = {auc_score:.3f}',
        xy=(0.65, 0.15),
        xycoords='axes fraction',
        fontsize=PlotStyle.ANNOTATION_SIZE + 2,
        fontweight='bold',
        color=PlotStyle.COLORS["primary"],
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=PlotStyle.COLORS["primary"], alpha=0.8)
    )
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str] = None,
    model_name: str = "Model",
    normalize: bool = False,
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot confusion matrix with annotations."""
    PlotStyle.apply_style()
    
    if class_names is None:
        class_names = ["No Disease", "Heart Disease"]
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fmt = '.2%'
        title = f'Normalized Confusion Matrix - {model_name}'
    else:
        fmt = 'd'
        title = f'Confusion Matrix - {model_name}'
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_MEDIUM)
    
    sns.heatmap(
        cm,
        annot=True,
        fmt=fmt,
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names,
        cbar_kws={'label': 'Proportion' if normalize else 'Count'},
        ax=ax,
        annot_kws={'size': PlotStyle.ANNOTATION_SIZE + 2, 'weight': 'bold'},
    )
    
    ax.set_xlabel('Predicted Label', fontweight='bold')
    ax.set_ylabel('True Label', fontweight='bold')
    ax.set_title(title, fontweight='bold', pad=15)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_feature_importance(
    importance: Dict[str, float],
    model_name: str = "Model",
    top_n: int = 15,
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot horizontal bar chart of feature importance."""
    PlotStyle.apply_style()
    
    # Sort and take top N
    sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    features = list(sorted_importance.keys())[::-1]  # Reverse for horizontal
    values = list(sorted_importance.values())[::-1]
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_WIDE)
    
    bars = ax.barh(
        features,
        values,
        color=PlotStyle.PALETTE[0],
        edgecolor='white',
        height=0.7,
        alpha=0.85
    )
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{value:.4f}',
            va='center',
            fontsize=PlotStyle.ANNOTATION_SIZE,
            fontweight='bold'
        )
    
    ax.set_xlabel('Importance Score', fontweight='bold')
    ax.set_ylabel('Feature', fontweight='bold')
    ax.set_title(f'Top {top_n} Feature Importance - {model_name}', fontweight='bold', pad=15)
    ax.set_xlim(0, max(values) * 1.15)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    model_name: str = "Dataset",
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot correlation heatmap for features."""
    PlotStyle.apply_style()
    
    corr = df.corr()
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_LARGE)
    
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Correlation Coefficient', 'shrink': 0.8},
        ax=ax,
        annot_kws={'size': PlotStyle.ANNOTATION_SIZE - 1},
    )
    
    ax.set_title(f'Feature Correlation Heatmap - {model_name}', fontweight='bold', pad=15)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_model_comparison(
    metrics_df: pd.DataFrame,
    metrics: List[str] = None,
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot grouped bar chart comparing models across metrics."""
    PlotStyle.apply_style()
    
    if metrics is None:
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    
    models = metrics_df['algorithm'].tolist()
    x = np.arange(len(models))
    width = 0.15
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_WIDE)
    
    for i, metric in enumerate(metrics):
        offset = (i - len(metrics) / 2 + 0.5) * width
        values = metrics_df[metric].tolist()
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=metric.replace('_', ' ').title(),
            color=PlotStyle.PALETTE[i % len(PlotStyle.PALETTE)],
            alpha=0.85,
            edgecolor='white'
        )
        
        # Add value labels
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f'{value:.3f}',
                ha='center',
                va='bottom',
                fontsize=PlotStyle.ANNOTATION_SIZE - 1,
                fontweight='bold'
            )
    
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Model Performance Comparison', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.set_ylim(0, 1.1)
    ax.legend(loc='lower right', ncol=2, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig


def plot_training_curves(
    train_scores: List[float],
    val_scores: List[float],
    param_name: str,
    param_values: List[Any],
    model_name: str = "Model",
    save_path: Optional[Path] = None,
    show: bool = True,
) -> plt.Figure:
    """Plot training/validation curves for hyperparameter tuning."""
    PlotStyle.apply_style()
    
    fig, ax = plt.subplots(figsize=PlotStyle.FIGSIZE_MEDIUM)
    
    ax.plot(
        param_values, train_scores,
        'o-', color=PlotStyle.COLORS["primary"],
        label='Training Score', linewidth=2, markersize=6
    )
    ax.plot(
        param_values, val_scores,
        's-', color=PlotStyle.COLORS["secondary"],
        label='Validation Score', linewidth=2, markersize=6
    )
    
    # Highlight best
    best_idx = np.argmax(val_scores)
    ax.axvline(
        x=param_values[best_idx],
        color=PlotStyle.COLORS["success"],
        linestyle='--',
        alpha=0.7,
        label=f'Best {param_name} = {param_values[best_idx]}'
    )
    
    ax.set_xlabel(param_name, fontweight='bold')
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title(f'Hyperparameter Tuning: {param_name} - {model_name}', fontweight='bold', pad=15)
    ax.legend(framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    if isinstance(param_values[0], (int, float)):
        ax.set_xscale('log' if max(param_values) / min(param_values) > 100 else 'linear')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return fig
```

---

## 🖥️ CLI Design

### Command Structure

```bash
heart-predictor --help
heart-predictor predict --help
heart-predictor train --help
heart-predictor evaluate --help
heart-predictor serve --help
```

### Commands

```python
# src/interfaces/cli/commands.py
import click
from pathlib import Path
from typing import Optional, List
import json

@click.group()
@click.version_option(version="1.0.0")
@click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
@click.option('--verbose', '-v', count=True, help='Verbosity level')
@click.pass_context
def cli(ctx, config, verbose):
    """Heart Disease Predictor - ML-powered cardiac risk assessment."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('patient_id', type=str)
@click.option('--features', '-f', type=str, help='JSON string or path to features file')
@click.option('--model', '-m', type=str, help='Model ID to use (default: best)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', type=click.Choice(['json', 'table', 'report']), default='table')
@click.option('--explain', is_flag=True, help='Include SHAP explanation')
@click.pass_context
def predict(ctx, patient_id, features, model, output, format, explain):
    """Predict heart disease risk for a single patient.
    
    Examples:
        heart-predictor predict PATIENT_001 --features '{"age": 63, "sex": 1, ...}'
        heart-predictor predict PATIENT_002 --features features.json --format report
    """
    from src.interfaces.cli.predict import run_prediction
    run_prediction(patient_id, features, model, output, format, explain, ctx.obj)


@cli.command()
@click.option('--algorithm', '-a', type=click.Choice([
    'logistic_regression', 'svm', 'random_forest', 'knn', 'kmeans', 'decision_tree'
]), multiple=True, help='Algorithms to train')
@click.option('--tune/--no-tune', default=False, help='Enable hyperparameter tuning')
@click.option('--cv-folds', type=int, default=5, help='Cross-validation folds')
@click.option('--test-size', type=float, default=0.2, help='Test set proportion')
@click.option('--output-dir', type=click.Path(), help='Output directory for models')
@click.pass_context
def train(ctx, algorithm, tune, cv_folds, test_size, output_dir):
    """Train machine learning models.
    
    Examples:
        heart-predictor train --algorithm logistic_regression --tune
        heart-predictor train -a svm -a random_forest --cv-folds 10
    """
    from src.interfaces.cli.train import run_training
    run_training(list(algorithm), tune, cv_folds, test_size, output_dir, ctx.obj)


@cli.command()
@click.option('--model', '-m', type=str, help='Model ID to evaluate (default: all)')
@click.option('--dataset', '-d', type=click.Path(exists=True), help='Test dataset path')
@click.option('--metrics', type=str, multiple=True, help='Metrics to compute')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--plot/--no-plot', default=True, help='Generate visualization plots')
@click.pass_context
def evaluate(ctx, model, dataset, metrics, output, plot):
    """Evaluate model performance.
    
    Examples:
        heart-predictor evaluate --model model_v1 --plot
        heart-predictor evaluate --metrics accuracy --metrics roc_auc
    """
    from src.interfaces.cli.evaluate import run_evaluation
    run_evaluation(model, dataset, list(metrics), output, plot, ctx.obj)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
@click.option('--workers', default=4, help='Number of worker processes')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.pass_context
def serve(ctx, host, port, workers, reload):
    """Start the REST API server.
    
    Examples:
        heart-predictor serve --port 8080 --workers 8
        heart-predictor serve --reload  # Development mode
    """
    from src.interfaces.cli.serve import run_server
    run_server(host, port, workers, reload, ctx.obj)


@cli.command()
@click.option('--algorithm', '-a', type=click.Choice([
    'logistic_regression', 'svm', 'random_forest', 'knn', 'kmeans', 'decision_tree'
]), multiple=True, help='Algorithms to compare')
@click.option('--metric', '-m', type=str, multiple=True, default=['accuracy', 'roc_auc'], help='Comparison metric')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def compare(ctx, algorithm, metric, output):
    """Compare multiple models.
    
    Examples:
        heart-predictor compare -a logistic_regression -a random_forest -a svm
        heart-predictor compare --metric f1_score --metric precision
    """
    from src.interfaces.cli.compare import run_comparison
    run_comparison(list(algorithm), list(metric), output, ctx.obj)


if __name__ == '__main__':
    cli()
```

---

## 🔗 Integration Patterns

### Event-Driven Architecture

```python
# src/shared/events/publisher.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class DomainEvent:
    event_type: str
    aggregate_id: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    def to_json(self) -> str:
        return json.dumps({
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
        })

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    def publish_batch(self, events: list[DomainEvent]) -> None:
        pass

# RabbitMQ Implementation
class RabbitMQEventPublisher(EventPublisher):
    def __init__(self, connection_url: str, exchange: str = "heart_disease"):
        self.connection_url = connection_url
        self.exchange = exchange
        self._connection = None
        self._channel = None
    
    def _ensure_connection(self):
        if self._connection is None or self._connection.is_closed:
            import pika
            self._connection = pika.BlockingConnection(
                pika.URLParameters(self.connection_url)
            )
            self._channel = self._connection.channel()
            self._channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
    
    def publish(self, event: DomainEvent) -> None:
        self._ensure_connection()
        routing_key = f"{event.event_type}.{event.aggregate_id}"
        self._channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=event.to_json(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json',
                headers={'version': event.version}
            )
        )
    
    def publish_batch(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.publish(event)
```

### Saga Pattern for Training Pipeline

```python
# src/features/model_training/application/sagas/training_saga.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import uuid

class TrainingStep(Enum):
    DATA_LOADING = "data_loading"
    PREPROCESSING = "preprocessing"
    MODEL_TRAINING = "model_training"
    EVALUATION = "evaluation"
    MODEL_REGISTRATION = "model_registration"
    NOTIFICATION = "notification"

@dataclass
class TrainingSagaState:
    saga_id: str
    current_step: TrainingStep
    completed_steps: List[TrainingStep]
    failed_step: Optional[TrainingStep]
    error_message: Optional[str]
    model_id: Optional[str]
    metrics: dict
    compensation_actions: List[callable]

class TrainingSaga:
    """Saga orchestrator for model training pipeline."""
    
    def __init__(self, services: dict):
        self.services = services
        self.state = TrainingSagaState(
            saga_id=str(uuid.uuid4()),
            current_step=TrainingStep.DATA_LOADING,
            completed_steps=[],
            failed_step=None,
            error_message=None,
            model_id=None,
            metrics={},
            compensation_actions=[]
        )
    
    def execute(self, config: TrainingConfig) -> TrainingResult:
        try:
            # Step 1: Data Loading
            self._execute_step(TrainingStep.DATA_LOADING, lambda: self._load_data(config))
            
            # Step 2: Preprocessing
            self._execute_step(TrainingStep.PREPROCESSING, lambda: self._preprocess(config))
            
            # Step 3: Model Training
            self._execute_step(TrainingStep.MODEL_TRAINING, lambda: self._train_model(config))
            
            # Step 4: Evaluation
            self._execute_step(TrainingStep.EVALUATION, lambda: self._evaluate_model(config))
            
            # Step 5: Model Registration
            self._execute_step(TrainingStep.MODEL_REGISTRATION, lambda: self._register_model(config))
            
            # Step 6: Notification
            self._execute_step(TrainingStep.NOTIFICATION, lambda: self._notify_completion(config))
            
            return TrainingResult(
                success=True,
                model_id=self.state.model_id,
                metrics=self.state.metrics,
                saga_id=self.state.saga_id
            )
            
        except Exception as e:
            self.state.failed_step = self.state.current_step
            self.state.error_message = str(e)
            self._compensate()
            return TrainingResult(
                success=False,
                error=str(e),
                saga_id=self.state.saga_id
            )
    
    def _execute_step(self, step: TrainingStep, action: callable):
        self.state.current_step = step
        result = action()
        self.state.completed_steps.append(step)
        return result
    
    def _compensate(self):
        for action in reversed(self.state.compensation_actions):
            try:
                action()
            except Exception:
                pass  # Log but continue compensation
```

---

## 📱 Mobile/Edge Considerations

### Model Optimization for Edge
```python
# src/features/prediction/infrastructure/optimization.py
import onnx
import onnxruntime as ort
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import numpy as np

class ModelOptimizer:
    """Optimize models for edge deployment."""
    
    @staticmethod
    def to_onnx(model, input_shape: tuple, output_path: str):
        """Convert sklearn model to ONNX format."""
        initial_type = [('float_input', FloatTensorType([None, input_shape[1]]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        onnx.save_model(onnx_model, output_path)
        return output_path
    
    @staticmethod
    def quantize_model(onnx_path: str, output_path: str):
        """Quantize ONNX model for faster inference."""
        from onnxruntime.quantization import quantize_dynamic, QuantType
        quantize_dynamic(
            onnx_path,
            output_path,
            weight_type=QuantType.QInt8
        )
        return output_path
    
    @staticmethod
    def benchmark(model_path: str, input_data: np.ndarray, runs: int = 100) -> dict:
        """Benchmark model inference."""
        import time
        
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name
        
        # Warmup
        for _ in range(10):
            session.run(None, {input_name: input_data.astype(np.float32)})
        
        # Benchmark
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            session.run(None, {input_name: input_data.astype(np.float32)})
            times.append((time.perf_counter() - start) * 1000)
        
        return {
            "mean_ms": np.mean(times),
            "std_ms": np.std(times),
            "min_ms": np.min(times),
            "max_ms": np.max(times),
            "p50_ms": np.percentile(times, 50),
            "p95_ms": np.percentile(times, 95),
            "p99_ms": np.percentile(times, 99),
        }
```

---

## 📋 Design Checklist

| Component | Status | Notes |
|-----------|--------|-------|
| Data Models | ✅ Defined | Pydantic schemas for all entities |
| API Contracts | ✅ Defined | OpenAPI 3.0 specification |
| Algorithm Interfaces | ✅ Defined | BaseAlgorithm + 6 implementations |
| Visualization | ✅ Defined | Consistent styling, 6 plot types |
| CLI Design | ✅ Defined | 6 commands with options |
| Event System | ✅ Defined | Domain events + RabbitMQ |
| Saga Pattern | ✅ Defined | Training pipeline orchestration |
| Edge Optimization | ✅ Defined | ONNX conversion + quantization |
| Database Schema | 📋 Planned | PostgreSQL + migrations |
| Authentication | 📋 Planned | JWT + RBAC |
| Rate Limiting | 📋 Planned | Token bucket algorithm |

---

*This document is part of Cycle 1 (SPECIFY) in the HIM-SPEC Three-Cycle Live Proof methodology.*