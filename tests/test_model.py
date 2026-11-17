# Integrantes: Camila N. Carniel - RA 10338558-0; Bruno G. Ramalho - RA 1042649-1.
# Conteúdo: testes da avaliação por grafo e das métricas dos estados parciais.
# Histórico de alterações:
# 17/11/2026 | Grupo | Inclusão dos testes do avaliador de baselines.

import pandas as pd

from len_eda.model import evaluate_feature_table


def test_evaluate_feature_table_keeps_graphs_separate(tmp_path):
    rows = []
    for graph_index in range(12):
        label = "campaign" if graph_index % 2 == 0 else "noncampaign"
        for fraction in (0.1, 0.2):
            rows.append(
                {
                    "file": f"graph_{graph_index}.json",
                    "topic": f"topic_{graph_index}",
                    "label": label,
                    "partiality_mode": "events",
                    "fraction": fraction,
                    "cutoff_timestamp": fraction,
                    "full_event_count": 100,
                    "node_count": 10 + graph_index * 2,
                    "edge_count": 20 + graph_index,
                }
            )
    frame = pd.DataFrame(rows)
    csv_path = tmp_path / "features.csv"
    frame.to_csv(csv_path, index=False)

    results = evaluate_feature_table(csv_path)

    assert len(results) == 4
    assert {row["model"] for row in results} == {
        "logistic_regression",
        "random_forest",
    }
    assert all(row["train_graphs"] + row["test_graphs"] == 12 for row in results)
