import json
import math

import pytest

from len_eda.summary import inspect_graph


def test_inspect_graph_computes_structural_and_temporal_metrics(tmp_path):
    graph = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": [
            {"id": 1, "node_attr": [0.1, 0.2], "author.description": math.nan},
            {"id": 2, "node_attr": [0.2, 0.3]},
            {"id": 3, "node_attr": [0.3, 0.4]},
        ],
        "links": [
            {
                "source": 1,
                "target": 2,
                "timestamp": 100,
                "Interaction_Count": 2,
                "edge_attr": [0.1],
            },
            {
                "source": 2,
                "target": 1,
                "timestamp": 110,
                "Interaction_Count": 1,
                "edge_attr": [0.2],
            },
            {
                "source": 2,
                "target": 3,
                "timestamp": 120,
                "Interaction_Count": 3,
                "edge_attr": [0.3],
            },
        ],
    }
    path = tmp_path / "topico___2023-01-01_campaign_fulldata.json"
    path.write_text(json.dumps(graph), encoding="utf-8")

    result = inspect_graph(path)

    assert result["topic"] == "topico"
    assert result["label"] == "campaign"
    assert result["nodes"] == 3
    assert result["edges"] == 3
    assert result["node_attr_dim"] == 2
    assert result["edge_attr_dim"] == 1
    assert result["density"] == pytest.approx(0.5)
    assert result["reciprocity"] == pytest.approx(2 / 3)
    assert result["weak_components"] == 1
    assert result["largest_weak_component_fraction"] == 1.0
    assert result["timestamp_coverage"] == 1.0
    assert result["duration_hours"] == pytest.approx(20 / 3600)
    assert result["interaction_count_sum"] == 6
