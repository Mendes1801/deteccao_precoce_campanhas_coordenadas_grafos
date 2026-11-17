# Integrantes: Camila N. Carniel - RA 10338558-0; Bruno G. Ramalho - RA 1042649-1.
# Conteúdo: avaliação reprodutível de baseline tabular por estado temporal e divisão por grafo.
# Histórico de alterações:
# 17/11/2026 | Grupo | Implementação de regressão logística, Random Forest e métricas por fração.

"""Baselines para classificação dos estados parciais do LEN."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


METADATA_COLUMNS = {
    "file",
    "topic",
    "label",
    "partiality_mode",
    "fraction",
    "cutoff_timestamp",
    "full_event_count",
}


def evaluate_feature_table(
    csv_path: str | Path,
    *,
    mode: str = "events",
) -> list[dict[str, object]]:
    """Avalia baselines por fração, mantendo grafos inteiros em cada divisão."""
    frame = pd.read_csv(csv_path)
    eligible = frame[frame["partiality_mode"].eq(mode)].copy()
    if eligible.empty:
        raise ValueError(f"Nenhuma linha encontrada para o modo parcial '{mode}'")

    rows: list[dict[str, object]] = []
    for fraction in sorted(eligible["fraction"].unique()):
        subset = eligible[eligible["fraction"].eq(fraction)].copy()
        subset["label_binary"] = subset["label"].map({"campaign": 1, "noncampaign": 0})
        subset = subset.dropna(subset=["label_binary"])

        feature_columns = [
            column
            for column in subset.select_dtypes(include=[np.number]).columns
            if column not in METADATA_COLUMNS | {"label_binary"}
        ]
        if not feature_columns:
            raise ValueError("A tabela não contém atributos numéricos utilizáveis")

        X = subset[feature_columns].replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median()).fillna(0.0)
        y = subset["label_binary"].astype(int)
        groups = subset["file"]

        if y.nunique() < 2:
            raise ValueError(f"A classe não tem os dois rótulos na fração {fraction}")

        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
        train_indices, test_indices = next(splitter.split(X, y, groups))

        models = {
            "logistic_regression": make_pipeline(
                StandardScaler(),
                LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        }

        for model_name, model in models.items():
            model.fit(X.iloc[train_indices], y.iloc[train_indices])
            prediction = model.predict(X.iloc[test_indices])
            probability = model.predict_proba(X.iloc[test_indices])[:, 1]
            truth = y.iloc[test_indices]
            rows.append(
                {
                    "model": model_name,
                    "partiality_mode": mode,
                    "fraction": fraction,
                    "train_graphs": len(set(groups.iloc[train_indices])),
                    "test_graphs": len(set(groups.iloc[test_indices])),
                    "balanced_accuracy": balanced_accuracy_score(truth, prediction),
                    "precision": precision_score(truth, prediction, zero_division=0),
                    "recall": recall_score(truth, prediction, zero_division=0),
                    "f1": f1_score(truth, prediction, zero_division=0),
                    "roc_auc": roc_auc_score(truth, probability),
                }
            )
    return rows


def write_evaluation(rows: Iterable[dict[str, object]], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows)[0].keys() if False else [
        "model",
        "partiality_mode",
        "fraction",
        "train_graphs",
        "test_graphs",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    ]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia baselines tabulares dos grafos parciais")
    parser.add_argument("--features", required=True, help="CSV gerado por len-features")
    parser.add_argument("--mode", choices=("time", "events"), default="events")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = evaluate_feature_table(args.features, mode=args.mode)
    write_evaluation(rows, args.output)


if __name__ == "__main__":
    main()
