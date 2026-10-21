"""Detecta comunidades de deputados a partir de votos nominais da Câmara."""

from __future__ import annotations

import argparse
import itertools
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import requests
from matplotlib.lines import Line2D
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
DATA_INICIO = "2023-08-01"
DATA_FIM = "2023-08-31"
LIMIAR_CONCORDANCIA = 0.70
MIN_VOTACOES_JUNTOS = 5


def criar_sessao() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({"Accept": "application/json"})
    return session


def obter_paginas(session: requests.Session, url: str) -> list[dict]:
    """Busca todos os itens de uma rota paginada da API."""
    itens: list[dict] = []
    proxima_url: str | None = url

    while proxima_url:
        resposta = session.get(proxima_url, timeout=30)
        resposta.raise_for_status()
        payload = resposta.json()
        itens.extend(payload.get("dados", []))
        proxima_url = next(
            (link["href"] for link in payload.get("links", []) if link.get("rel") == "next"),
            None,
        )

    return itens


def coletar_votacoes(
    session: requests.Session, limite: int | None = None
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    url = (
        f"{API_BASE}/votacoes?dataInicio={DATA_INICIO}&dataFim={DATA_FIM}"
        "&ordem=ASC&ordenarPor=dataHoraRegistro&itens=100"
    )
    votacoes = obter_paginas(session, url)
    if limite is not None:
        votacoes = votacoes[:limite]

    print(f"Encontradas {len(votacoes)} votações para processar. Baixando votos nominais...")
    votos_deputados: dict[str, dict[str, str]] = defaultdict(dict)
    partidos_deputados: dict[str, str] = {}

    for indice, votacao in enumerate(votacoes, start=1):
        id_votacao = votacao["id"]
        votos = obter_paginas(session, f"{API_BASE}/votacoes/{id_votacao}/votos")

        for voto in votos:
            deputado = voto.get("deputado_") or {}
            nome = deputado.get("nome")
            partido = deputado.get("siglaPartido") or "Sem partido"
            tipo_voto = voto.get("tipoVoto")
            if not nome or not tipo_voto:
                continue

            identificador = f"{nome} ({partido})"
            votos_deputados[identificador][id_votacao] = tipo_voto
            partidos_deputados[identificador] = partido

        if indice % 100 == 0 or indice == len(votacoes):
            print(f"Votos nominais consultados: {indice}/{len(votacoes)}")

    return votos_deputados, partidos_deputados


def construir_grafo(
    votos_deputados: dict[str, dict[str, str]], partidos_deputados: dict[str, str]
) -> nx.Graph:
    grafo = nx.Graph()
    grafo.graph.update(
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM,
        limiar_concordancia=LIMIAR_CONCORDANCIA,
        min_votacoes_juntos=MIN_VOTACOES_JUNTOS,
    )
    for deputado, partido in partidos_deputados.items():
        grafo.add_node(deputado, partido=partido)

    deputados = list(votos_deputados)
    for deputado1, deputado2 in itertools.combinations(deputados, 2):
        votos1 = votos_deputados[deputado1]
        votos2 = votos_deputados[deputado2]
        votacoes_comuns = votos1.keys() & votos2.keys()

        if len(votacoes_comuns) < MIN_VOTACOES_JUNTOS:
            continue

        concordancias = sum(votos1[id_votacao] == votos2[id_votacao] for id_votacao in votacoes_comuns)
        taxa_concordancia = concordancias / len(votacoes_comuns)
        if taxa_concordancia >= LIMIAR_CONCORDANCIA:
            grafo.add_edge(deputado1, deputado2, weight=taxa_concordancia)

    return grafo


def detectar_comunidades(grafo: nx.Graph) -> list[set[str]]:
    comunidades = nx.community.louvain_communities(grafo, weight="weight", seed=42)
    comunidades_ordenadas = sorted(comunidades, key=lambda grupo: (-len(grupo), sorted(grupo)))
    for indice, comunidade in enumerate(comunidades_ordenadas, start=1):
        for deputado in comunidade:
            grafo.nodes[deputado]["comunidade"] = indice
    return comunidades_ordenadas


def salvar_grafos(
    grafo: nx.Graph, comunidades: list[set[str]], pasta_saida: Path
) -> None:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_graphml = pasta_saida / "rede_deputados.graphml"
    caminho_gexf = pasta_saida / "rede_deputados.gexf"
    caminho_csv = pasta_saida / "comunidades_deputados.csv"
    caminho_jpeg = pasta_saida / "rede_deputados.jpg"

    nx.write_graphml(grafo, caminho_graphml)
    nx.write_gexf(grafo, caminho_gexf)
    salvar_visualizacao(grafo, comunidades, caminho_jpeg)

    linhas = [
        {
            "deputado": deputado,
            "partido": grafo.nodes[deputado]["partido"],
            "comunidade": indice,
            "grau": grafo.degree(deputado),
        }
        for indice, comunidade in enumerate(comunidades, start=1)
        for deputado in sorted(comunidade)
    ]
    pd.DataFrame(
        linhas, columns=["deputado", "partido", "comunidade", "grau"]
    ).to_csv(caminho_csv, index=False, encoding="utf-8")
    print(f"Arquivos salvos em: {pasta_saida}")
    print(f"- {caminho_graphml.name}")
    print(f"- {caminho_gexf.name}")
    print(f"- {caminho_csv.name}")
    print(f"- {caminho_jpeg.name}")


def salvar_visualizacao(
    grafo: nx.Graph,
    comunidades: list[set[str]],
    caminho: Path,
    destaques: list[str] | None = None,
) -> None:
    fig, ax = plt.subplots(
        figsize=(22, 14) if destaques else (18, 14), facecolor="white"
    )
    ax.set_axis_off()
    fig.suptitle("Rede de concordância nos votos da Câmara", fontsize=21, y=0.97)
    if destaques:
        fig.subplots_adjust(right=0.73)
        fig.text(0.75, 0.88, "MAIORES PONTES ESTRUTURAIS", fontsize=12, weight="bold")
        for indice, deputado in enumerate(destaques[:10]):
            fig.text(0.755, 0.83 - indice * 0.045, f"{indice + 1:02d}. {deputado}", fontsize=9)
        fig.text(
            0.75,
            0.32,
            "Estrela: top 10 por intermediação\n"
            "ponderada. As cores representam\n"
            "as comunidades detectadas.\n\n"
            "A métrica indica posição de ponte\n"
            "na rede de votos, não comprova\n"
            "influência informal.",
            fontsize=9,
            va="top",
            color="#475467",
        )

    if grafo.number_of_nodes() == 0:
        ax.text(0.5, 0.5, "Nenhum voto nominal no período", ha="center", va="center")
        fig.savefig(caminho, format="jpeg", dpi=220, bbox_inches="tight")
        plt.close(fig)
        return

    paleta = plt.get_cmap("tab10").colors
    graus = dict(grafo.degree())
    grau_maximo = max(graus.values(), default=1)
    maior_comunidade = max((len(grupo) for grupo in comunidades), default=1)
    posicoes: dict[str, tuple[float, float]] = {}

    for indice, comunidade in enumerate(comunidades):
        if indice < 2 and len(comunidades) > 1:
            centro_x = -1.65 if indice == 0 else 1.65
            centro_y = 0.65
            raio_grupo = 1.8
        else:
            indice_menor = indice - min(2, len(comunidades))
            quantidade_menores = len(comunidades) - min(2, len(comunidades))
            centro_x = (indice_menor - (quantidade_menores - 1) / 2) * 0.95
            centro_y = -2.0
            raio_grupo = 0.25 + 0.9 * math.sqrt(len(comunidade) / maior_comunidade)
        nos = sorted(comunidade)
        for posicao, deputado in enumerate(nos):
            raio = raio_grupo * math.sqrt((posicao + 0.5) / len(nos))
            angulo = posicao * math.pi * (3 - math.sqrt(5))
            posicoes[deputado] = (
                centro_x + raio * math.cos(angulo),
                centro_y + raio * math.sin(angulo),
            )

    nx.draw_networkx_edges(
        grafo,
        posicoes,
        ax=ax,
        edge_color="#667085",
        width=0.25,
        alpha=0.012,
    )

    legenda = []
    for indice, comunidade in enumerate(comunidades):
        cor = paleta[indice % len(paleta)]
        nos = sorted(comunidade)
        tamanhos = [8 + 18 * (graus[no] / grau_maximo) ** 0.5 for no in nos]
        nx.draw_networkx_nodes(
            grafo,
            posicoes,
            nodelist=nos,
            node_size=tamanhos,
            node_color=[cor],
            edgecolors="white",
            linewidths=0.25,
            alpha=0.95,
            ax=ax,
        )
        legenda.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                color=cor,
                markersize=8,
                label=f"Comunidade {indice + 1}: {len(nos)} deputados",
            )
        )

    if destaques:
        destaques_presentes = [no for no in destaques[:10] if no in grafo]
        nx.draw_networkx_nodes(
            grafo,
            posicoes,
            nodelist=destaques_presentes,
            node_shape="*",
            node_size=150,
            node_color="#17202a",
            edgecolors="white",
            linewidths=0.8,
            ax=ax,
        )

    ax.legend(
        handles=legenda,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.04),
        ncol=min(4, max(1, len(legenda))),
        frameon=False,
        fontsize=10,
    )
    ax.set_title(
        f"{grafo.number_of_nodes()} deputados | {grafo.number_of_edges():,} arestas | "
        f"{grafo.graph.get('data_inicio', DATA_INICIO)} a "
        f"{grafo.graph.get('data_fim', DATA_FIM)}\n"
        f"Aresta: concordância >= {LIMIAR_CONCORDANCIA:.0%} em pelo menos "
        f"{MIN_VOTACOES_JUNTOS} votações compartilhadas",
        fontsize=12,
        pad=18,
    )
    fig.savefig(caminho, format="jpeg", dpi=220, bbox_inches="tight")
    plt.close(fig)


def exibir_comunidades(
    comunidades: list[set[str]], partidos_deputados: dict[str, str]
) -> None:

    print("\n--- RESULTADOS DA DETECÇÃO ---")
    for indice, comunidade in enumerate(comunidades, start=1):
        partidos = [partidos_deputados[deputado] for deputado in comunidade]
        contagem_partidos = pd.Series(partidos).value_counts().to_dict()
        exemplos = sorted(comunidade)[:5]
        print(f"\nComunidade {indice} ({len(comunidade)} deputados):")
        print(f"Principais partidos: {contagem_partidos}")
        print(f"Exemplos de membros: {exemplos}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limite-votacoes",
        type=int,
        help="Limita a quantidade de votações para um teste rápido da API.",
    )
    parser.add_argument(
        "--pasta-saida",
        type=Path,
        default=Path(__file__).resolve().parent / "grafos",
        help="Pasta onde serão gravados o grafo e a tabela de comunidades.",
    )
    args = parser.parse_args()

    print(f"Buscando votações entre {DATA_INICIO} e {DATA_FIM}...")
    with criar_sessao() as session:
        votos_deputados, partidos_deputados = coletar_votacoes(
            session, limite=args.limite_votacoes
        )

    grafo = construir_grafo(votos_deputados, partidos_deputados)
    print(f"Grafo construído: {grafo.number_of_nodes()} nós e {grafo.number_of_edges()} arestas.")
    print("Detectando comunidades com algoritmo de Louvain...")
    comunidades = detectar_comunidades(grafo)
    salvar_grafos(grafo, comunidades, args.pasta_saida)
    exibir_comunidades(comunidades, partidos_deputados)


if __name__ == "__main__":
    main()