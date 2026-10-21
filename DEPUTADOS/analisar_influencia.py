"""Rankeia deputados por intermediação estrutural na rede de votos."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

from rede_votacoes import salvar_visualizacao


PASTA_GRAFOS = Path(__file__).resolve().parent / "grafos"


def analisar_grafo(caminho_grafo: Path) -> tuple[nx.Graph, pd.DataFrame]:
    grafo = nx.read_graphml(caminho_grafo)
    comunidades_por_no: dict[str, int] = {}

    for deputado, atributos in grafo.nodes(data=True):
        comunidade = int(atributos["comunidade"])
        atributos["comunidade"] = comunidade
        comunidades_por_no[deputado] = comunidade

    for _, _, atributos in grafo.edges(data=True):
        concordancia = float(atributos["weight"])
        atributos["weight"] = concordancia
        atributos["distance"] = 1 / concordancia

    betweenness = nx.betweenness_centrality(
        grafo, normalized=True, weight="distance"
    )
    linhas = []

    for deputado in grafo:
        comunidade = comunidades_por_no[deputado]
        total_por_comunidade: Counter[int] = Counter()
        peso_por_comunidade: Counter[int] = Counter()
        for vizinho, atributos in grafo[deputado].items():
            comunidade_vizinha = comunidades_por_no[vizinho]
            total_por_comunidade[comunidade_vizinha] += 1
            peso_por_comunidade[comunidade_vizinha] += atributos["weight"]

        grau = grafo.degree(deputado)
        grau_externo = sum(
            quantidade
            for comunidade_vizinha, quantidade in total_por_comunidade.items()
            if comunidade_vizinha != comunidade
        )
        forca_externa = sum(
            peso
            for comunidade_vizinha, peso in peso_por_comunidade.items()
            if comunidade_vizinha != comunidade
        )
        forca_total = sum(peso_por_comunidade.values())
        participacao_ponderada = (
            1
            - sum((peso / forca_total) ** 2 for peso in peso_por_comunidade.values())
            if forca_total
            else 0.0
        )

        linhas.append(
            {
                "deputado": deputado,
                "partido": grafo.nodes[deputado].get("partido", ""),
                "comunidade": comunidade,
                "intermediacao_ponderada": betweenness[deputado],
                "grau": grau,
                "ligacoes_outras_comunidades": grau_externo,
                "fracao_ligacoes_externas": grau_externo / grau if grau else 0.0,
                "forca_concordancia_externa": forca_externa,
                "participacao_ponderada": participacao_ponderada,
            }
        )

    ranking = pd.DataFrame(linhas).sort_values(
        ["intermediacao_ponderada", "forca_concordancia_externa"],
        ascending=[False, False],
        ignore_index=True,
    )
    ranking.insert(0, "posicao", range(1, len(ranking) + 1))
    return grafo, ranking


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grafo",
        type=Path,
        default=PASTA_GRAFOS / "rede_deputados.graphml",
        help="Arquivo GraphML da rede de votos.",
    )
    parser.add_argument(
        "--pasta-saida",
        type=Path,
        default=PASTA_GRAFOS,
        help="Pasta para salvar o ranking CSV e o grafo JPEG.",
    )
    args = parser.parse_args()

    grafo, ranking = analisar_grafo(args.grafo)
    args.pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_csv = args.pasta_saida / "ranking_influencia_estrutural.csv"
    caminho_jpeg = args.pasta_saida / "grafo_influencia_bastidor.jpg"
    ranking.to_csv(caminho_csv, index=False, encoding="utf-8")

    comunidades = [
        set(ranking.loc[ranking["comunidade"] == comunidade, "deputado"])
        for comunidade in sorted(ranking["comunidade"].unique())
    ]
    destaques = ranking.head(10)["deputado"].tolist()
    salvar_visualizacao(grafo, comunidades, caminho_jpeg, destaques=destaques)

    print("Dez maiores intermediações ponderadas:")
    for linha in ranking.head(10).itertuples(index=False):
        print(
            f"{linha.posicao}. {linha.deputado} | "
            f"intermediação={linha.intermediacao_ponderada:.6f} | "
            f"conexões externas={linha.ligacoes_outras_comunidades}/"
            f"{linha.grau} ({linha.fracao_ligacoes_externas:.1%})"
        )
    print(f"Ranking CSV: {caminho_csv}")
    print(f"Grafo JPEG: {caminho_jpeg}")


if __name__ == "__main__":
    main()