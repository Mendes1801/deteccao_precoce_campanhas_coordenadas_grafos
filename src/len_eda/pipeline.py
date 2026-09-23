"""Gera uma tabela de features para estados parciais dos grafos do LEN."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .features import extract_features
from .summary import _filename_metadata
from .temporal import partial_graph, read_temporal_graph


DEFAULT_FRACTIONS = tuple(step / 10 for step in range(1, 11))


def load_exclusions(path: str | Path | None) -> set[str]:
    if path is None:
        return set()
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return {
            row["file"]
            for row in csv.DictReader(stream)
            if row.get("exclude", "").strip().lower() in {"1", "true", "yes", "sim"}
        }


def build_feature_table(
    data_dir: str | Path,
    *,
    fractions: tuple[float, ...] = DEFAULT_FRACTIONS,
    modes: tuple[str, ...] = ("time", "events"),
    exclusions: set[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, object]]:
    exclusions = exclusions or set()
    paths = [
        path
        for path in sorted(Path(data_dir).glob("*.json"))
        if path.name not in exclusions
    ]
    if limit is not None:
        paths = paths[:limit]
    if not paths:
        raise FileNotFoundError(f"Nenhum JSON elegível encontrado em {data_dir}")

    rows: list[dict[str, object]] = []
    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] {path.name}", file=sys.stderr, flush=True)
        graph = read_temporal_graph(path)
        topic, label = _filename_metadata(path)
        for mode in modes:
            for fraction in fractions:
                snapshot = partial_graph(graph, fraction, mode)  # type: ignore[arg-type]
                row: dict[str, object] = {
                    "file": path.name,
                    "topic": topic,
                    "label": label,
                    "partiality_mode": mode,
                    "fraction": fraction,
                    "cutoff_timestamp": snapshot.graph["cutoff_timestamp"],
                    "full_event_count": snapshot.graph["full_event_count"],
                }
                row.update(extract_features(snapshot))
                rows.append(row)
    return rows


def write_feature_table(rows: list[dict[str, object]], output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        # Os tópicos do Twitter frequentemente começam com ``#``. Alguns
        # visualizadores de CSV tratam linhas iniciadas por ``#`` como
        # comentários e escondem esses registros. QUOTE_NONNUMERIC mantém os
        # campos de texto entre aspas e evita essa interpretação sem transformar
        # as métricas numéricas em texto.
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
            quoting=csv.QUOTE_NONNUMERIC,
        )
        writer.writeheader()
        writer.writerows(rows)
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("small_encoder_final"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exclusions", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=("time", "events"),
        default=("time", "events"),
    )
    parser.add_argument(
        "--fractions",
        nargs="+",
        type=float,
        default=DEFAULT_FRACTIONS,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_feature_table(
        args.data_dir,
        fractions=tuple(args.fractions),
        modes=tuple(args.modes),
        exclusions=load_exclusions(args.exclusions),
        limit=args.limit,
    )
    output = write_feature_table(rows, args.output)
    print(f"{len(rows)} estados parciais salvos em {output}")


if __name__ == "__main__":
    main()
