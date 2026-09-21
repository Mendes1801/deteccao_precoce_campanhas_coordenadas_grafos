import networkx as nx
import pytest

from len_eda.features import extract_features
from len_eda.temporal import partial_graph


def test_extract_features_uses_only_partial_graph():
    graph = nx.DiGraph()
    graph.add_edge(1, 2, timestamp=100, Interaction_Count=2)
    graph.add_edge(2, 1, timestamp=110, Interaction_Count=1)
    graph.add_edge(2, 3, timestamp=200, Interaction_Count=5)

    partial = partial_graph(graph, 2 / 3, "events")
    features = extract_features(partial)

    assert features["nodes"] == 2
    assert features["edges"] == 2
    assert features["interaction_count_sum"] == 3
    assert features["reciprocity"] == 1.0
    assert features["largest_weak_component_fraction"] == 1.0
    assert features["observed_span_hours"] == pytest.approx(10 / 3600)
