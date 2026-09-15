# Integrantes: preencher com nome completo, e-mail e RA de cada integrante.
# Conteúdo: leitura incremental dos grafos JSON do LEN e cálculo das métricas da EDA.
# Histórico de alterações:
# 15/09/2026 | Grupo | Criação do leitor incremental e das métricas estruturais e temporais.

"""Inspeção incremental dos grafos JSON do LEN.

Os arquivos codificados com LaBSE são grandes principalmente por causa dos
vetores de atributos. Este módulo usa um parser incremental para calcular
métricas simples sem materializar esses vetores na memória.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any, Iterable

import ijson


CAMPAIGN_SUFFIX = "_campaign_fulldata.json"
NONCAMPAIGN_SUFFIX = "_noncampaign_fulldata.json"
NON_STANDARD_NUMBER = re.compile(rb"-?Infinity|NaN")


class _SanitizedJsonReader:
    """Adapta constantes numéricas não padronizadas para JSON válido.

    Alguns arquivos do LEN usam ``NaN``. O parser incremental é estrito e, por
    isso, esses tokens são transformados em ``null`` somente no fluxo de leitura.
    Os arquivos originais não são modificados.
    """

    _CHUNK_SIZE = 1024 * 1024
    _OVERLAP = len(b"-Infinity") - 1

    def __init__(self, raw_stream: Any) -> None:
        self.raw_stream = raw_stream
        self.pending_raw = b""
        self.output = b""
        self.finished = False

    @staticmethod
    def _split_and_sanitize(data: bytes) -> tuple[bytes, bytes]:
        safe_cut = max(0, len(data) - _SanitizedJsonReader._OVERLAP)
        for match in NON_STANDARD_NUMBER.finditer(data):
            if match.start() < safe_cut:
                safe_cut = max(safe_cut, match.end())
        safe = NON_STANDARD_NUMBER.sub(b"null", data[:safe_cut])
        return safe, data[safe_cut:]

    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b""
        requested = self._CHUNK_SIZE if size < 0 else size

        while len(self.output) < requested and not self.finished:
            chunk = self.raw_stream.read(max(self._CHUNK_SIZE, requested))
            if chunk:
                sanitized, self.pending_raw = self._split_and_sanitize(
                    self.pending_raw + chunk
                )
                self.output += sanitized
            else:
                self.output += NON_STANDARD_NUMBER.sub(b"null", self.pending_raw)
                self.pending_raw = b""
                self.finished = True

        if size < 0:
            result, self.output = self.output, b""
            return result
        result = self.output[:size]
        self.output = self.output[size:]
        return result


def _filename_metadata(path: Path) -> tuple[str, str]:
    """Retorna o tópico e a classe codificados no nome do arquivo."""
    name = path.name
    if name.endswith(NONCAMPAIGN_SUFFIX):
        return name[: -len(NONCAMPAIGN_SUFFIX)], "noncampaign"
    if name.endswith(CAMPAIGN_SUFFIX):
        topic = name[: -len(CAMPAIGN_SUFFIX)]
        if "___" in topic:
            topic = topic.rsplit("___", 1)[0]
        elif "__" in topic:
            topic = topic.rsplit("__", 1)[0]
        return topic, "campaign"
    return path.stem, "unknown"


def _iso_utc(timestamp: int | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


class _UnionFind:
    def __init__(self, nodes: Iterable[Any]) -> None:
        self.parent = {node: node for node in nodes}
        self.size = {node: 1 for node in nodes}

    def find(self, node: Any) -> Any:
        parent = self.parent[node]
        while parent != self.parent[parent]:
            self.parent[parent] = self.parent[self.parent[parent]]
            parent = self.parent[parent]
        while node != parent:
            next_node = self.parent[node]
            self.parent[node] = parent
            node = next_node
        return parent

    def union(self, left: Any, right: Any) -> None:
        if left not in self.parent or right not in self.parent:
            return
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if self.size[root_left] < self.size[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        self.size[root_left] += self.size[root_right]

    def component_sizes(self) -> list[int]:
        counts = Counter(self.find(node) for node in self.parent)
        return list(counts.values())


def inspect_graph(path: str | Path) -> dict[str, Any]:
    """Calcula métricas estruturais e temporais básicas de um JSON LEN."""
    path = Path(path)
    topic, label = _filename_metadata(path)

    directed: bool | None = None
    multigraph: bool | None = None
    node_count = 0
    node_ids: set[Any] = set()
    node_attr_dim: int | None = None
    node_attr_counter = 0
    counting_node_attr = False

    edge_count = 0
    edge_attr_dim: int | None = None
    edge_attr_counter = 0
    counting_edge_attr = False
    current_edge: dict[str, Any] | None = None
    edges: list[tuple[Any, Any]] = []
    edge_pairs: set[tuple[Any, Any]] = set()
    in_degree: Counter[Any] = Counter()
    out_degree: Counter[Any] = Counter()
    self_loops = 0
    timestamp_missing = 0
    timestamps: list[int] = []
    timestamps_non_decreasing = True
    previous_timestamp: int | None = None
    interaction_sum = 0.0
    interaction_max = 0.0

    with path.open("rb") as raw_stream:
        stream = _SanitizedJsonReader(raw_stream)
        for prefix, event, value in ijson.parse(stream):
            if prefix == "directed" and event == "boolean":
                directed = bool(value)
            elif prefix == "multigraph" and event == "boolean":
                multigraph = bool(value)
            elif prefix == "nodes.item" and event == "start_map":
                node_count += 1
            elif prefix == "nodes.item.id" and event in {"number", "string"}:
                node_ids.add(value)
            elif (
                prefix == "nodes.item.node_attr"
                and event == "start_array"
                and node_attr_dim is None
            ):
                counting_node_attr = True
                node_attr_counter = 0
            elif prefix == "nodes.item.node_attr.item" and counting_node_attr:
                node_attr_counter += 1
            elif prefix == "nodes.item.node_attr" and event == "end_array" and counting_node_attr:
                node_attr_dim = node_attr_counter
                counting_node_attr = False
            elif prefix == "links.item" and event == "start_map":
                current_edge = {}
            elif current_edge is not None and prefix in {
                "links.item.source",
                "links.item.target",
                "links.item.timestamp",
                "links.item.Interaction_Count",
            } and event in {"number", "string", "null"}:
                current_edge[prefix.rsplit(".", 1)[-1]] = value
            elif (
                prefix == "links.item.edge_attr"
                and event == "start_array"
                and edge_attr_dim is None
            ):
                counting_edge_attr = True
                edge_attr_counter = 0
            elif prefix == "links.item.edge_attr.item" and counting_edge_attr:
                edge_attr_counter += 1
            elif prefix == "links.item.edge_attr" and event == "end_array" and counting_edge_attr:
                edge_attr_dim = edge_attr_counter
                counting_edge_attr = False
            elif prefix == "links.item" and event == "end_map" and current_edge is not None:
                edge_count += 1
                source = current_edge.get("source")
                target = current_edge.get("target")
                if source is not None and target is not None:
                    edges.append((source, target))
                    edge_pairs.add((source, target))
                    out_degree[source] += 1
                    in_degree[target] += 1
                    if source == target:
                        self_loops += 1

                raw_timestamp = current_edge.get("timestamp")
                if raw_timestamp is None:
                    timestamp_missing += 1
                else:
                    timestamp = int(raw_timestamp)
                    timestamps.append(timestamp)
                    if previous_timestamp is not None and timestamp < previous_timestamp:
                        timestamps_non_decreasing = False
                    previous_timestamp = timestamp

                raw_interactions = current_edge.get("Interaction_Count")
                if raw_interactions is not None:
                    interactions = float(raw_interactions)
                    interaction_sum += interactions
                    interaction_max = max(interaction_max, interactions)
                current_edge = None

    union_find = _UnionFind(node_ids)
    for source, target in edges:
        union_find.union(source, target)
    component_sizes = union_find.component_sizes()

    degrees = [in_degree[node] + out_degree[node] for node in node_ids]
    reciprocal_edges = sum(
        (target, source) in edge_pairs
        for source, target in edge_pairs
        if source != target
    )
    non_loop_edges = edge_count - self_loops
    density_denominator = node_count * (node_count - 1)
    timestamp_min = min(timestamps, default=None)
    timestamp_max = max(timestamps, default=None)
    duration_seconds = (
        timestamp_max - timestamp_min
        if timestamp_min is not None and timestamp_max is not None
        else None
    )
    missing_endpoints = sum(
        source not in node_ids or target not in node_ids for source, target in edges
    )

    return {
        "file": path.name,
        "topic": topic,
        "label": label,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
        "directed": directed,
        "multigraph": multigraph,
        "nodes": node_count,
        "unique_node_ids": len(node_ids),
        "duplicate_node_ids": node_count - len(node_ids),
        "edges": edge_count,
        "unique_edge_pairs": len(edge_pairs),
        "self_loops": self_loops,
        "missing_edge_endpoints": missing_endpoints,
        "node_attr_dim": node_attr_dim,
        "edge_attr_dim": edge_attr_dim,
        "density": non_loop_edges / density_denominator if density_denominator else 0.0,
        "mean_total_degree": fmean(degrees) if degrees else 0.0,
        "std_total_degree": pstdev(degrees) if len(degrees) > 1 else 0.0,
        "max_total_degree": max(degrees, default=0),
        "reciprocity": reciprocal_edges / non_loop_edges if non_loop_edges else 0.0,
        "weak_components": len(component_sizes),
        "largest_weak_component_nodes": max(component_sizes, default=0),
        "largest_weak_component_fraction": (
            max(component_sizes, default=0) / node_count if node_count else 0.0
        ),
        "timestamps_present": len(timestamps),
        "timestamps_missing": timestamp_missing,
        "timestamp_coverage": len(timestamps) / edge_count if edge_count else 0.0,
        "unique_timestamps": len(set(timestamps)),
        "timestamps_non_decreasing_in_file": timestamps_non_decreasing,
        "timestamp_start_utc": _iso_utc(timestamp_min),
        "timestamp_end_utc": _iso_utc(timestamp_max),
        "duration_hours": duration_seconds / 3600 if duration_seconds is not None else math.nan,
        "interaction_count_sum": interaction_sum,
        "interaction_count_mean": interaction_sum / edge_count if edge_count else 0.0,
        "interaction_count_max": interaction_max,
    }


def inspect_directory(data_dir: str | Path, limit: int | None = None) -> list[dict[str, Any]]:
    paths = sorted(Path(data_dir).glob("*.json"))
    if limit is not None:
        paths = paths[:limit]
    if not paths:
        raise FileNotFoundError(f"Nenhum JSON encontrado em {data_dir}")

    rows = []
    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] {path.name}", file=sys.stderr, flush=True)
        rows.append(inspect_graph(path))
    return rows


def write_csv(rows: list[dict[str, Any]], output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output


def _print_overview(rows: list[dict[str, Any]]) -> None:
    labels = Counter(row["label"] for row in rows)
    print(f"Grafos processados: {len(rows)}")
    print("Classes: " + ", ".join(f"{label}={count}" for label, count in sorted(labels.items())))
    print(f"Nós: {sum(row['nodes'] for row in rows):,}")
    print(f"Arestas: {sum(row['edges'] for row in rows):,}")
    print(
        "Cobertura temporal mínima: "
        f"{min(row['timestamp_coverage'] for row in rows):.2%}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="small_encoder_final", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = inspect_directory(args.data_dir, args.limit)
    _print_overview(rows)
    if args.output:
        output = write_csv(rows, args.output)
        print(f"Resumo salvo em: {output}")


if __name__ == "__main__":
    main()
