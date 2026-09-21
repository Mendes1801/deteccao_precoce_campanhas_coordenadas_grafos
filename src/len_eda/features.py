"""Características estruturais e temporais de um estado parcial do LEN."""

from __future__ import annotations

import math
from collections.abc import Iterable
from statistics import fmean, median, pstdev
from typing import Any

import networkx as nx


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _gini(values: Iterable[float]) -> float:
    ordered = sorted(max(0.0, float(value)) for value in values)
    total = sum(ordered)
    if not ordered or total == 0:
        return 0.0
    weighted = sum((index + 1) * value for index, value in enumerate(ordered))
    return (2 * weighted) / (len(ordered) * total) - (len(ordered) + 1) / len(ordered)


def _summary(prefix: str, values: Iterable[float]) -> dict[str, float]:
    values = [float(value) for value in values]
    return {
        f"{prefix}_mean": fmean(values) if values else math.nan,
        f"{prefix}_std": pstdev(values) if len(values) > 1 else 0.0,
        f"{prefix}_median": median(values) if values else math.nan,
        f"{prefix}_p90": _quantile(values, 0.90),
        f"{prefix}_max": max(values, default=math.nan),
        f"{prefix}_gini": _gini(values),
    }


def _temporal_distribution(timestamps: list[float], bins: int = 10) -> dict[str, float]:
    if not timestamps:
        return {
            "temporal_entropy": math.nan,
            "temporal_peak_share": math.nan,
            "simultaneous_event_share": math.nan,
        }
    start, end = min(timestamps), max(timestamps)
    counts = [0] * bins
    if end == start:
        counts[0] = len(timestamps)
    else:
        for timestamp in timestamps:
            index = min(bins - 1, int((timestamp - start) / (end - start) * bins))
            counts[index] += 1
    probabilities = [count / len(timestamps) for count in counts if count]
    entropy = -sum(p * math.log(p) for p in probabilities) / math.log(bins)
    unique = len(set(timestamps))
    return {
        "temporal_entropy": entropy,
        "temporal_peak_share": max(counts) / len(timestamps),
        "simultaneous_event_share": 1 - unique / len(timestamps),
    }


def extract_features(graph: nx.DiGraph) -> dict[str, Any]:
    """Calcula features reproduzíveis sem consultar o grafo futuro."""

    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    self_loops = nx.number_of_selfloops(graph)
    non_loop_edges = m - self_loops
    denominator = n * (n - 1)

    in_degrees = [degree for _, degree in graph.in_degree()]
    out_degrees = [degree for _, degree in graph.out_degree()]
    total_degrees = [graph.in_degree(node) + graph.out_degree(node) for node in graph]

    weak = list(nx.weakly_connected_components(graph)) if n else []
    strong = list(nx.strongly_connected_components(graph)) if n else []
    reciprocal = sum(
        graph.has_edge(target, source)
        for source, target in graph.edges()
        if source != target
    )

    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes())
    undirected.add_edges_from((u, v) for u, v in graph.edges() if u != v)
    if undirected.number_of_edges():
        communities = nx.community.louvain_communities(undirected, seed=42)
        modularity = nx.community.modularity(undirected, communities)
        average_clustering = nx.average_clustering(undirected)
        transitivity = nx.transitivity(undirected)
    else:
        communities = [{node} for node in undirected]
        modularity = 0.0
        average_clustering = 0.0
        transitivity = 0.0

    timestamps = [float(data["timestamp"]) for _, _, data in graph.edges(data=True)]
    ordered_timestamps = sorted(timestamps)
    gaps = [right - left for left, right in zip(ordered_timestamps, ordered_timestamps[1:])]
    interactions = [
        float(data.get("Interaction_Count", 0)) for _, _, data in graph.edges(data=True)
    ]

    observed_span = (
        max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.0
    )
    full_start = graph.graph.get("full_start_timestamp", min(timestamps, default=math.nan))
    cutoff = graph.graph.get("cutoff_timestamp", max(timestamps, default=math.nan))
    window_seconds = (
        max(0.0, float(cutoff) - float(full_start))
        if not math.isnan(float(full_start)) and not math.isnan(float(cutoff))
        else math.nan
    )
    rate_hours = window_seconds / 3600 if window_seconds and window_seconds > 0 else math.nan

    features: dict[str, Any] = {
        "nodes": n,
        "edges": m,
        "interaction_count_sum": sum(interactions),
        "self_loops": self_loops,
        "self_loop_fraction": self_loops / m if m else 0.0,
        "density": non_loop_edges / denominator if denominator else 0.0,
        "reciprocity": reciprocal / non_loop_edges if non_loop_edges else 0.0,
        "weak_components": len(weak),
        "largest_weak_component_fraction": max(map(len, weak), default=0) / n if n else 0.0,
        "strong_components": len(strong),
        "largest_strong_component_fraction": max(map(len, strong), default=0) / n if n else 0.0,
        "communities": len(communities),
        "modularity": modularity,
        "average_clustering": average_clustering,
        "transitivity": transitivity,
        "max_in_degree_centralization": max(in_degrees, default=0) / (n - 1) if n > 1 else 0.0,
        "max_out_degree_centralization": max(out_degrees, default=0) / (n - 1) if n > 1 else 0.0,
        "unique_timestamps": len(set(timestamps)),
        "observed_span_hours": observed_span / 3600,
        "observation_window_hours": window_seconds / 3600 if not math.isnan(window_seconds) else math.nan,
        "edges_per_hour": m / rate_hours if rate_hours else math.nan,
        "nodes_per_hour": n / rate_hours if rate_hours else math.nan,
        "interactions_per_hour": sum(interactions) / rate_hours if rate_hours else math.nan,
    }
    features.update(_summary("in_degree", in_degrees))
    features.update(_summary("out_degree", out_degrees))
    features.update(_summary("total_degree", total_degrees))
    features.update(_summary("interaction_count", interactions))
    features.update(_summary("interevent_seconds", gaps))
    mean_gap = features["interevent_seconds_mean"]
    std_gap = features["interevent_seconds_std"]
    features["burstiness"] = (
        (std_gap - mean_gap) / (std_gap + mean_gap)
        if not math.isnan(mean_gap) and std_gap + mean_gap > 0
        else 0.0
    )
    features.update(_temporal_distribution(timestamps))
    return features
