"""CLI:  python -m cardioscreen {train|predict|serve}"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from . import config


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cardioscreen", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("train", help="compare all models, save the best")
    p = sub.add_parser("predict", help="predict for one patient")
    for f in config.FEATURES:
        p.add_argument(f"--{f.name}", type=float if f.name == "oldpeak" else int, required=True, help=f.description)
    s = sub.add_parser("serve", help="run the web app")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.cmd == "train":
        from .train import train

        r = train()
        d = r["dataset"]
        print(f"\nData: {d['raw_rows']} rows -> {d['unique_patients']} unique patients "
              f"({d['duplicates_removed']} duplicates removed)\n")
        print(f"{'Model':<22}{'CV AUC':>8}{'Test AUC':>10}{'Acc':>7}{'Sens':>7}{'Spec':>7}")
        for m in r["comparison"]:
            print(f"{m['model']:<22}{m['cv_roc_auc']:>8.3f}{m['test_roc_auc']:>10.3f}"
                  f"{m['test_accuracy']:>7.3f}{m['test_recall_sensitivity']:>7.3f}{m['test_specificity']:>7.3f}")
        print(f"\nSelected: {r['selected_model']}  (saved to {config.MODEL_PATH})")
    elif args.cmd == "predict":
        from .predictor import Predictor
        from .schemas import PatientFeatures

        patient = PatientFeatures(**{f: getattr(args, f) for f in config.FEATURE_NAMES})
        print(json.dumps(Predictor.load().predict(patient).model_dump(), indent=2))
    elif args.cmd == "serve":
        import uvicorn

        uvicorn.run("cardioscreen.api:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())