"""Reconstrução de estados parciais dos grafos temporais do LEN.

O LEN preserva somente a interação mais recente de cada par ordenado. Portanto,
uma aresta é tratada aqui como um *evento observado* no timestamp armazenado; o
código não tenta inventar os horários das interações anteriores resumidas em
``Interaction_Count``.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Literal

import ijson
import networkx as nx

from .summary import _SanitizedJsonReader


PartialityMode = Literal["time", "events"]


def read_temporal_graph(path: str | Path) -> nx.DiGraph:
    """Lê somente os campos necessários à reconstrução temporal de um JSON LEN.

    Os vetores LaBSE e os atributos derivados do grafo completo são ignorados.
    Isso reduz o uso de memória e impede o uso acidental de ``kcore``.
    """

    path = Path(path)
    graph = nx.DiGraph(source_file=path.name)
    current: dict[str, Any] | None = None
    wanted = {"source", "target", "timestamp", "Interaction_Count"}

    with path.open("rb") as raw_stream:
        stream = _SanitizedJsonReader(raw_stream)
        for prefix, event, value in ijson.parse(stream):
            if prefix == "links.item" and event == "start_map":
                current = {}
            elif (
                current is not None
                and prefix.startswith("links.item.")
                and prefix.rsplit(".", 1)[-1] in wanted
                and event in {"number", "string", "null"}
            ):
                current[prefix.rsplit(".", 1)[-1]] = value
            elif prefix == "links.item" and event == "end_map" and current is not None:
                source = current.get("source")
                target = current.get("target")
                timestamp = current.get("timestamp")
                if source is not None and target is not None and timestamp is not None:
                    graph.add_edge(
                        source,
                        target,
                        timestamp=int(timestamp),
                        Interaction_Count=float(current.get("Interaction_Count") or 0),
                    )
                current = None

    return graph


def _validate_fraction(fraction: float) -> float:
    fraction = float(fraction)
    if not 0 < fraction <= 1:
        raise ValueError("fraction deve estar no intervalo (0, 1]")
    return fraction


def partial_graph(
    graph: nx.DiGraph,
    fraction: float,
    mode: PartialityMode,
    *,
    timestamp_attr: str = "timestamp",
) -> nx.DiGraph:
    """Retorna um grafo parcial contendo somente nós que já interagiram.

    ``mode='time'`` usa uma fração da duração total observada. ``mode='events'``
    usa a fração das arestas/eventos observados em ordem cronológica. Em caso de
    empate temporal, a ordenação original do NetworkX é usada como desempate
    estável. A função nunca copia nós isolados do grafo completo, pois eles ainda
    não seriam conhecidos em um cenário de detecção precoce.
    """

    fraction = _validate_fraction(fraction)
    if mode not in {"time", "events"}:
        raise ValueError("mode deve ser 'time' ou 'events'")

    edges = list(graph.edges(data=True))
    if any(timestamp_attr not in data for _, _, data in edges):
        raise ValueError(f"todas as arestas devem possuir o atributo {timestamp_attr!r}")

    ordered = sorted(
        enumerate(edges),
        key=lambda item: (float(item[1][2][timestamp_attr]), item[0]),
    )
    start = min((float(e[2][timestamp_attr]) for e in edges), default=math.nan)
    end = max((float(e[2][timestamp_attr]) for e in edges), default=math.nan)

    if not edges:
        selected: list[tuple[Any, Any, dict[str, Any]]] = []
        cutoff = math.nan
    elif mode == "time":
        cutoff = start + fraction * (end - start)
        selected = [edge for _, edge in ordered if float(edge[2][timestamp_attr]) <= cutoff]
    else:
        count = max(1, math.ceil(fraction * len(ordered)))
        selected = [edge for _, edge in ordered[:count]]
        cutoff = float(selected[-1][2][timestamp_attr])

    partial = graph.__class__()
    partial.graph.update(graph.graph)
    partial.graph.update(
        partiality_mode=mode,
        partiality_fraction=fraction,
        full_start_timestamp=start,
        full_end_timestamp=end,
        cutoff_timestamp=cutoff,
        full_event_count=len(edges),
    )
    for source, target, data in selected:
        if source in graph:
            partial.add_node(source, **graph.nodes[source])
        if target in graph:
            partial.add_node(target, **graph.nodes[target])
        partial.add_edge(source, target, **data)
    return partial
