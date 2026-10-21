"""Gera uma visualização interativa em PyVis a partir do grafo de concordância dos deputados."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
from pyvis.network import Network

PASTA_BASE = Path(__file__).resolve().parent
PASTA_GRAFOS = PASTA_BASE / "grafos"
ARQUIVO_GRAFO = PASTA_GRAFOS / "rede_deputados.graphml"
ARQUIVO_HTML = PASTA_GRAFOS / "rede_deputados_pyvis.html"

PALETA = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc949",
    "#af7aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ab",
]


def carregar_grafo(caminho: Path) -> nx.Graph:
    grafo = nx.read_graphml(caminho)
    for nome, atributos in grafo.nodes(data=True):
        comunidade = int(atributos.get("comunidade", 1))
        atributos["comunidade"] = comunidade
        atributos["partido"] = atributos.get("partido", "Sem partido")
        atributos["titulo"] = (
            f"<b>{nome}</b><br>"
            f"Partido: {atributos['partido']}<br>"
            f"Comunidade: {comunidade}<br>"
            f"Grau: {grafo.degree(nome)}"
        )
    return grafo


def obter_cor_comunidade(comunidade: int) -> str:
    return PALETA[comunidade % len(PALETA)]


def main() -> None:
    PASTA_GRAFOS.mkdir(parents=True, exist_ok=True)
    grafo = carregar_grafo(ARQUIVO_GRAFO)

    rede = Network(
        height="920px",
        width="100%",
        directed=False,
        bgcolor="#ffffff",
        font_color="#1f2937",
        notebook=False,
        cdn_resources="remote",
    )

    rede.set_options(
        """
        {
          "layout": {
            "improvedLayout": true,
            "hierarchical": false,
            "clusterThreshold": 150
          },
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -3500,
              "centralGravity": 0.25,
              "springLength": 220,
              "springConstant": 0.08,
              "damping": 0.15,
              "avoidOverlap": 0.7
            },
            "minVelocity": 0.75,
            "solver": "barnesHut"
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 120,
            "multiselect": true,
            "navigationButtons": true,
            "dragNodes": true,
            "selectConnectedEdges": true
          },
          "nodes": {
            "borderWidth": 1,
            "borderWidthSelected": 2,
            "shape": "dot",
            "size": 18,
            "font": {
              "size": 12,
              "face": "Arial",
              "align": "center"
            }
          },
          "edges": {
            "smooth": true,
            "color": {
              "color": "#7a7f87",
              "highlight": "#1f2937",
              "hover": "#374151",
              "inherit": false
            },
            "width": 1,
            "selectionWidth": 2,
            "arrows": {
              "to": false,
              "from": false
            }
          }
        }
        """
    )

    for deputado, atributos in grafo.nodes(data=True):
        comunidade = int(atributos.get("comunidade", 1))
        grau = grafo.degree(deputado)
        tamanho = 12 + min(32, grau * 2.5)
        rede.add_node(
            deputado,
            label=deputado.split(" (")[0],
            title=atributos["titulo"],
            size=tamanho,
            color={
                "background": obter_cor_comunidade(comunidade),
                "border": "#1f2937",
                "highlight": {
                    "background": "#facc15",
                    "border": "#111827",
                },
            },
            value=grau,
            group=comunidade,
            shape="dot",
            mass=grau / max(1, grafo.number_of_edges()),
        )

    for deputado1, deputado2, atributos in grafo.edges(data=True):
        peso = float(atributos.get("weight", 1.0))
        titulo = f"Concordância: {peso:.2f}"
        rede.add_edge(
            deputado1,
            deputado2,
            title=titulo,
            value=peso,
            width=max(1.0, min(7.0, peso * 10.0)),
            label="",
            color="#7a7f87",
        )

    rede.save_graph(str(ARQUIVO_HTML))
    print(f"Visualização PyVis salva em: {ARQUIVO_HTML}")
    print(f"Nós: {grafo.number_of_nodes()} | Arestas: {grafo.number_of_edges()}")
    print("Abra o arquivo em um navegador para explorar a rede.")


if __name__ == "__main__":
    main()
