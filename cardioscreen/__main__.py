"""CLI: python -m cardioscreen {train|predict|serve}"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from . import config
from .services.model_service import ModelService
from .services.training_service import TrainingService
from .models.schemas import PatientFeatures


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cardioscreen", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Train command
    train_parser = sub.add_parser("train", help="compare all models, save the best")
    train_parser.add_argument("--data", type=str, help="Path to training data CSV")
    train_parser.add_argument("--model", type=str, help="Path to save model")
    train_parser.add_argument("--reports", type=str, help="Path to save reports")
    train_parser.add_argument("--only", nargs="+", help="Only train specific models")

    # Predict command
    predict_parser = sub.add_parser("predict", help="predict for one patient")
    for f in config.FEATURES:
        predict_parser.add_argument(
            f"--{f.name}",
            type=float if f.name == "oldpeak" else int,
            required=True,
            help=f.description,
        )

    # Serve command
    serve_parser = sub.add_parser("serve", help="run the web app")
    serve_parser.add_argument("--host", default=config.settings.api_host)
    serve_parser.add_argument("--port", type=int, default=config.settings.api_port)
    serve_parser.add_argument("--workers", type=int, default=config.settings.api_workers)

    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.cmd == "train":
        training_service = TrainingService()
        result = training_service.train(
            data_path=args.data,
            model_path=args.model,
            reports_dir=args.reports,
            only=args.only,
        )
        d = result.dataset_info
        print(f"\nData: {d['raw_rows']} rows -> {d['unique_patients']} unique patients "
              f"({d['duplicates_removed']} duplicates removed)\n")
        print(f"{'Model':<22}{'CV AUC':>8}{'Test AUC':>10}{'Acc':>7}{'Sens':>7}{'Spec':>7}")
        for m in result.comparison:
            print(f"{m['model']:<22}{m['cv_roc_auc']:>8.3f}{m['test_roc_auc']:>10.3f}"
                  f"{m['test_accuracy']:>7.3f}{m['test_recall_sensitivity']:>7.3f}{m['test_specificity']:>7.3f}")
        print(f"\nSelected: {result.selected_model}  (saved to {args.model or config.settings.model_path})")

    elif args.cmd == "predict":
        patient = PatientFeatures(**{f: getattr(args, f) for f in config.FEATURE_NAMES})
        service = ModelService().load()
        print(json.dumps(service.predict(patient).model_dump(), indent=2))

    elif args.cmd == "serve":
        import uvicorn
        uvicorn.run(
            "cardioscreen.api:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())