"""Training CLI entry point using new service structure."""

from __future__ import annotations

from ..services.training_service import TrainingService
from ..core.config import settings


def train(
    data_path: str | None = None,
    model_path: str | None = None,
    reports_dir: str | None = None,
    only: list[str] | None = None,
) -> dict:
    """Run the full comparison and persist the winner. Returns the metrics dict."""
    training_service = TrainingService()
    result = training_service.train(
        data_path=data_path,
        model_path=model_path,
        reports_dir=reports_dir,
        only=only,
    )
    return {
        "dataset": result.dataset_info,
        "selected_model": result.selected_model,
        "selection_criterion": result.selection_criterion,
        "comparison": result.comparison,
        "sklearn_version": result.sklearn_version,
    }


if __name__ == "__main__":
    train()