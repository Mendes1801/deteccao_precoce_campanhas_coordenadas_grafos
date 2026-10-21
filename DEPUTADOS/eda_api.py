"""EDA delimitado da API da Câmara; não faz exportação anual nem define o tema."""
from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from camara_api import CamaraAPI


def select_sample(rows, n, seed=42):
    """Amostra reproduzível, com ordenação cronológica apenas para apresentação."""
    selected = random.Random(seed).sample(rows, min(n, len(rows)))
    return sorted(selected, key=lambda x: (x.get("data", ""), str(x.get("id", ""))))


def collect(api, inicio, fim, n_votacoes=30, n_proposicoes=12):
    catalogue = {}
    data = {"inicio": inicio, "fim": fim, "seed": 42, "catalogo": catalogue,
            "coleta_iniciada_em": datetime.now(timezone.utc).isoformat(), "erros": []}

    def listing(name, path, params=None, pages=1):
        records, info = api.list(path, params, max_pages=pages)
        catalogue[name] = {**info, "rota": path, "filtros": params, "registros": len(records)}
        data[name] = records
        return records

    # Recorte igual ao script já existente: agosto/2023. Órgão resolvido por sigla.
    orgaos = listing("orgaos", "/orgaos", {"sigla": "PLEN", "itens": 100})
    plen = next((x for x in orgaos if x.get("sigla") == "PLEN"), None)
    if not plen:
        raise RuntimeError("Plenário não localizado pela API.")
    listing("deputados", "/deputados", {"dataInicio": inicio, "dataFim": fim,
            "itens": 100, "ordenarPor": "id", "ordem": "ASC"}, pages=10)
    votacoes = listing("votacoes", "/votacoes", {"dataInicio": inicio, "dataFim": fim,
            "idOrgao": plen["id"], "itens": 100, "ordenarPor": "dataHoraRegistro", "ordem": "ASC"}, pages=10)
    listing("proposicoes", "/proposicoes", {"siglaTipo": "PL", "dataApresentacaoInicio": inicio,
            "dataApresentacaoFim": fim, "itens": 100, "ordenarPor": "id", "ordem": "ASC"})
    listing("eventos", "/eventos", {"dataInicio": inicio, "dataFim": fim,
            "itens": 100, "ordenarPor": "dataHoraInicio", "ordem": "ASC"})
    listing("temas_referencia", "/referencias/proposicoes/codTema")

    # Enriquecimento deliberado por descrição com placar: NÃO é amostra aleatória do mês.
    # Também inspecionamos descrições sem placar para verificar cobertura/ausências.
    with_score = [v for v in votacoes if re.search(r"\bSim\s*:\s*\d", v.get("descricao") or "", re.I)]
    without_score = [v for v in votacoes if v not in with_score]
    selected = select_sample(with_score, n_votacoes) + select_sample(without_score, 6, seed=43)
    data["amostragem"] = {"universo_metadados": len(votacoes),
        "descricoes_com_placar": len(with_score), "descricoes_sem_placar": len(without_score),
        "selecionadas_com_placar": min(n_votacoes, len(with_score)),
        "selecionadas_sem_placar": min(6, len(without_score)),
        "metodo": "Aleatória semente 42 dentro das descrições com placar; semente 43 nas demais. Amostra exploratória enriquecida, não representativa da produção legislativa."}
    data["votacoes_consultadas"] = selected
    jobs = []
    for v in selected:
        jobs.append(("votos", str(v["id"]), f"/votacoes/{v['id']}/votos", None, 10))
    props = select_sample(data["proposicoes"], n_proposicoes)
    data["proposicoes_consultadas"] = props
    for p in props:
        for resource in ["autores", "temas", "tramitacoes"]:
            jobs.append((resource, str(p["id"]), f"/proposicoes/{p['id']}/{resource}", None, 1))
    data["consultas"] = []

    def run(job):
        kind, identifier, path, params, pages = job
        try:
            records, info = api.list(path, params, pages)
            return {"tipo": kind, "id": identifier, "rota": path, "dados": records, **info}
        except (Exception,) as exc:
            # Falhas são mantidas no relatório; não viram zeros de atividade.
            return {"tipo": kind, "id": identifier, "rota": path, "dados": [],
                    "status": "erro", "completo": False, "erro": str(exc)}

    print(f"Metadados: {len(votacoes)} votações. Consultas delimitadas: {len(jobs)}.", flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for i, result in enumerate(pool.map(run, jobs), 1):
            data["consultas"].append(result)
            if result["status"] == "erro":
                data["erros"].append(result)
            if i % 10 == 0:
                print(f"Consultas concluídas: {i}/{len(jobs)}", flush=True)

    successful = [x for x in data["consultas"] if x["tipo"] == "votos" and x["status"] == 200 and x["dados"]]
    secondary = [("orientacoes", x["id"], f"/votacoes/{x['id']}/orientacoes", None, 10) for x in successful[:24]]
    # Despesas: demonstração de campos, sem comparação de pessoas ou totalização populacional.
    deputy_pool = sorted({v.get("deputado_", {}).get("id") for x in successful for v in x["dados"] if v.get("deputado_", {}).get("id")})
    deputy_ids = random.Random(44).sample(deputy_pool, min(3, len(deputy_pool)))
    for identifier in deputy_ids:
        secondary.append(("despesas", str(identifier), f"/deputados/{identifier}/despesas",
                          {"ano": inicio[:4], "mes": int(inicio[5:7]), "itens": 100}, 1))
    for event in data["eventos"][:3]:
        secondary.append(("presencas", str(event["id"]), f"/eventos/{event['id']}/deputados", None, 1))
    # Detalhes para conhecer a relação votação -> objetos e proposições afetadas.
    for x in successful[:5]:
        rec = api.get(f"/votacoes/{x['id']}")
        data.setdefault("detalhes_votacoes", []).append({"id": x["id"], **rec})
    with ThreadPoolExecutor(max_workers=3) as pool:
        data["consultas"].extend(pool.map(run, secondary))
    data["requisicoes"] = api.log
    return data


def quality_table(data):
    rows = []
    for name in ["deputados", "votacoes", "proposicoes", "eventos"]:
        frame = pd.json_normalize(data[name])
        for col in frame:
            empty = frame[col].isna() | frame[col].map(lambda x: isinstance(x, str) and not x.strip())
            rows.append({"recurso": name, "campo": col, "registros": len(frame),
                         "ausentes": int(empty.sum()), "fracao_ausente": float(empty.mean())})
    return pd.DataFrame(rows)


def vote_frame(data):
    rows = []
    dates = {str(x["id"]): (x.get("data", ""), x.get("dataHoraRegistro", "")) for x in data["votacoes"]}
    for q in data["consultas"]:
        if q["tipo"] != "votos" or q["status"] != 200 or not q["completo"]:
            continue
        for vote in q["dados"]:
            deputy = vote.get("deputado_") or {}
            rows.append({"idVotacao": q["id"], "idDeputado": deputy.get("id"),
                         "nome": deputy.get("nome"), "partido": deputy.get("siglaPartido"),
                         "uf": deputy.get("siglaUf"), "voto": vote.get("tipoVoto"),
                         "dataVotacao": dates.get(q["id"], ("", ""))[0],
                         "ordemRegistroVotacao": dates.get(q["id"], ("", ""))[1],
                         "dataRegistroVoto": vote.get("dataRegistroVoto")})
    return pd.DataFrame(rows, columns=["idVotacao", "idDeputado", "nome", "partido", "uf", "voto", "dataVotacao", "ordemRegistroVotacao", "dataRegistroVoto"]).sort_values(["dataVotacao", "ordemRegistroVotacao", "idVotacao"])


def pair_matrices(votes):
    import numpy as np
    unique = votes.dropna(subset=["idDeputado", "voto"]).drop_duplicates(["idDeputado", "idVotacao"])
    conflicts = votes.groupby(["idDeputado", "idVotacao"])["voto"].nunique()
    bad = set(conflicts[conflicts > 1].index)
    unique = unique[[tuple(x) not in bad for x in unique[["idDeputado", "idVotacao"]].itertuples(index=False, name=None)]]
    if unique.empty:
        return [], np.zeros((0, 0), dtype=int), np.zeros((0, 0), dtype=float)
    pivot = unique.pivot(index="idDeputado", columns="idVotacao", values="voto")
    present = pivot.notna().to_numpy(dtype=np.int32)
    shared = present @ present.T
    same = np.zeros_like(shared)
    for kind in unique.voto.unique():
        indicators = (pivot == kind).to_numpy(dtype=np.int32)
        same += indicators @ indicators.T
    rates = np.divide(same, shared, out=np.full(shared.shape, np.nan), where=shared > 0)
    return list(pivot.index), shared, rates


def make_graph(ids, shared, rates, threshold, min_shared):
    import networkx as nx
    import numpy as np
    graph = nx.Graph()
    graph.add_nodes_from(int(x) for x in ids)
    for i, j in zip(*np.where(np.triu((shared >= min_shared) & (rates >= threshold), 1))):
        graph.add_edge(int(ids[i]), int(ids[j]), weight=float(rates[i, j]), n_comuns=int(shared[i, j]))
    return graph


def analyse(data, out):
    import numpy as np
    import networkx as nx
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import adjusted_rand_score

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    figures = out / "figuras"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    quality = quality_table(data)
    quality.to_csv(out / "qualidade_campos.csv", index=False)
    votes = vote_frame(data)
    votes.to_csv(out / "votos_amostra.csv", index=False)
    pd.DataFrame(data["votacoes"]).to_csv(out / "votacoes_metadados.csv", index=False)
    pd.DataFrame([{k: v for k, v in q.items() if k != "dados"} | {"registros": len(q["dados"])} for q in data["consultas"]]).to_csv(out / "cobertura_consultas.csv", index=False)
    if votes.empty:
        raise RuntimeError("Nenhum voto disponível na amostra; consulte cobertura_consultas.csv.")
    duplicates = int(votes.duplicated(["idVotacao", "idDeputado"]).sum())
    conflicts = int((votes.groupby(["idVotacao", "idDeputado"])["voto"].nunique() > 1).sum())
    # Duplicatas conflitantes não são escolhidas arbitrariamente.
    conflicting_keys = votes.groupby(["idVotacao", "idDeputado"])["voto"].nunique()
    conflicting_keys = set(conflicting_keys[conflicting_keys > 1].index)
    valid = votes.dropna(subset=["idDeputado", "voto"]).copy()
    valid = valid[[tuple(x) not in conflicting_keys for x in valid[["idVotacao", "idDeputado"]].itertuples(index=False, name=None)]]
    valid = valid.drop_duplicates(["idVotacao", "idDeputado"])
    binary = valid[valid.voto.isin(["Sim", "Não"])].copy()
    totals = binary.groupby(["idVotacao", "voto"]).size().unstack(fill_value=0).reindex(columns=["Sim", "Não"], fill_value=0)
    totals["total_binario"] = totals.sum(axis=1)
    totals["fracao_minoria"] = totals[["Sim", "Não"]].min(axis=1) / totals.total_binario
    totals.to_csv(out / "consenso_votacoes.csv")
    contested_ids = totals.index[totals.fracao_minoria >= .10]
    contested = binary[binary.idVotacao.isin(contested_ids)]
    names = valid.groupby("idDeputado")["nome"].last().to_dict()
    # Partido observado no próprio voto, nunca rótulo atual aplicado a todo o passado.
    parties = valid.groupby("idDeputado")["partido"].last().fillna("Sem informação").to_dict()
    party_changes = int((valid.groupby("idDeputado").partido.nunique() > 1).sum())

    graph_rows, graph_choices = [], {}
    for mode, subset in [("Todos os tipos", valid), ("Somente Sim/Não", binary), ("Sim/Não e minoria >=10%", contested)]:
        ids, shared, rates = pair_matrices(subset)
        for minimum in (5, 10, 20):
            for threshold in (.70, .80, .90):
                graph = make_graph(ids, shared, rates, threshold, minimum)
                active = graph.subgraph([n for n, degree in graph.degree if degree > 0]).copy()
                # Louvain apenas nas três redes de referência; demais células
                # medem sensibilidade de cobertura/densidade sem repetir a etapa cara.
                if active.number_of_edges() and minimum == 5 and threshold == .70:
                    communities = nx.community.louvain_communities(active, seed=42, weight="weight")
                    modularity = nx.community.modularity(active, communities, weight="weight")
                    labels = {n: i for i, c in enumerate(communities) for n in c}
                    comparable = [n for n in active if parties.get(n) and parties[n] != "Sem informação"]
                    ari = adjusted_rand_score([parties[n] for n in comparable], [labels[n] for n in comparable]) if len(comparable) > 1 else None
                else:
                    communities, modularity, ari = [], None, None
                graph_rows.append({"tratamento": mode, "minimo_comuns": minimum, "limiar": threshold,
                    "votacoes": subset.idVotacao.nunique(), "nos": len(graph), "arestas": graph.number_of_edges(),
                    "isolados": nx.number_of_isolates(graph), "densidade": nx.density(graph),
                    "comunidades_sem_isolados": len(communities) if modularity is not None else None, "modularidade": modularity,
                    "ARI_partidos": ari})
                if mode == "Somente Sim/Não" and minimum == 5 and threshold == .70:
                    graph_choices["base"] = (graph, communities)
                if mode == "Sim/Não e minoria >=10%" and minimum == 5 and threshold == .70:
                    graph_choices["controversas"] = (graph, communities)
    sensitivity = pd.DataFrame(graph_rows)
    sensitivity.to_csv(out / "sensibilidade_grafos.csv", index=False)
    graph, communities = graph_choices["base"]
    labels = {n: i + 1 for i, c in enumerate(communities) for n in c}
    for n in graph:
        graph.nodes[n].update(nome=str(names.get(n, n)), partido=str(parties.get(n, "Sem informação")), comunidade=labels.get(n, 0))
    nx.write_graphml(graph, out / "rede_amostra.graphml")
    community_frame = pd.DataFrame([{"idDeputado": n, **graph.nodes[n]} for n in graph])
    community_frame.to_csv(out / "comunidades_amostra.csv", index=False)
    composition = pd.crosstab(community_frame.partido, community_frame.comunidade)
    composition.to_csv(out / "comunidades_por_partido.csv")

    # Concordância agregada por pares de partidos; sem interpretar como ideologia.
    ids, shared, rates = pair_matrices(binary)
    upper = np.triu(shared >= 5, 1)
    agreement = []
    for i, j in zip(*np.where(upper)):
        a, b = sorted([parties.get(ids[i], "Sem informação"), parties.get(ids[j], "Sem informação")])
        agreement.append({"partidoA": a, "partidoB": b, "concordancia": rates[i, j], "n_comuns": shared[i, j]})
    grouped = pd.DataFrame(agreement).groupby(["partidoA", "partidoB"]).agg(
        concordancia_media=("concordancia", "mean"), pares=("concordancia", "size"),
        comuns_medio=("n_comuns", "mean")).reset_index() if agreement else pd.DataFrame()
    grouped.to_csv(out / "concordancia_partidos.csv", index=False)

    orientation_rows, orientation_coverage = [], []
    for q in data["consultas"]:
        if q["tipo"] != "orientacoes":
            continue
        orientation_coverage.append({"idVotacao": q["id"], "status": q["status"], "registros": len(q["dados"])})
        for o in q["dados"]:
            if o.get("codTipoLideranca") == "P":
                orientation_rows.append({"idVotacao": q["id"], "partido": o.get("siglaPartidoBloco"),
                                         "orientacao": o.get("orientacaoVoto")})
    ori = pd.DataFrame(orientation_rows, columns=["idVotacao", "partido", "orientacao"])
    ori.to_csv(out / "orientacoes_amostra.csv", index=False)
    orientations_unique = ori.drop_duplicates()
    orientation_conflicts = orientations_unique.groupby(["idVotacao", "partido"]).orientacao.nunique()
    orientation_bad = set(orientation_conflicts[orientation_conflicts > 1].index)
    orientations_unique = orientations_unique[[tuple(x) not in orientation_bad for x in orientations_unique[["idVotacao", "partido"]].itertuples(index=False, name=None)]]
    joined = binary.merge(orientations_unique, on=["idVotacao", "partido"], how="left", validate="many_to_one")
    comparable = joined[joined.orientacao.isin(["Sim", "Não"])].copy()
    comparable["concorda"] = comparable.voto == comparable.orientacao
    discipline = comparable.groupby("partido").agg(votos_comparaveis=("concorda", "size"),
        taxa_adesao=("concorda", "mean")).reset_index()
    discipline.to_csv(out / "adesao_orientacao_direta.csv", index=False)

    author_rows, theme_rows = [], []
    for q in data["consultas"]:
        if q["status"] != 200:
            continue
        for r in q["dados"]:
            if q["tipo"] == "autores":
                author_rows.append({"idProposicao": q["id"], **r})
            elif q["tipo"] == "temas":
                theme_rows.append({"idProposicao": q["id"], **r})
    pd.DataFrame(author_rows).to_csv(out / "autores_proposicoes_amostra.csv", index=False)
    pd.DataFrame(theme_rows).to_csv(out / "temas_proposicoes_amostra.csv", index=False)
    authors_by_prop = Counter(x["idProposicao"] for x in author_rows)
    themes_by_prop = Counter(x["idProposicao"] for x in theme_rows)
    expenses = [{"idDeputado": q["id"], **r} for q in data["consultas"] if q["tipo"] == "despesas" and q["status"] == 200 for r in q["dados"]]
    pd.DataFrame(expenses).to_csv(out / "despesas_amostra.csv", index=False)
    proceedings = [{"idProposicao": q["id"], **r} for q in data["consultas"] if q["tipo"] == "tramitacoes" and q["status"] == 200 for r in q["dados"]]
    pd.DataFrame(proceedings).to_csv(out / "tramitacoes_amostra.csv", index=False)

    # Figuras descritivas; legenda e tamanho do recorte explícitos.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    valid.voto.value_counts().sort_values().plot.barh(ax=axes[0], color="#3274a1")
    axes[0].set(title="Tipos de voto na amostra", xlabel="Registros")
    axes[1].hist(totals.fracao_minoria, bins=10, color="#3274a1", edgecolor="white")
    axes[1].axvline(.10, color="#c44e52", linestyle="--")
    axes[1].set(title="Quanto as votações dividem os votos?", xlabel="Fração minoritária entre Sim e Não", ylabel="Votações")
    pd.Series(valid.groupby("idDeputado").idVotacao.nunique()).plot.hist(ax=axes[2], bins=15, color="#55a868")
    axes[2].set(title="Cobertura por deputado", xlabel="Votações com registro na amostra", ylabel="Deputados")
    fig.suptitle(f"EDA exploratório — {data['inicio']} a {data['fim']} — Plenário", fontsize=13)
    fig.tight_layout()
    fig.savefig(figures / "01_cobertura_e_votos.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    base_sens = sensitivity[(sensitivity.tratamento == "Somente Sim/Não") & (sensitivity.minimo_comuns == 5)]
    axes[0].plot(base_sens.limiar, base_sens.densidade, "o-", label="Todas Sim/Não")
    cont_sens = sensitivity[(sensitivity.tratamento == "Sim/Não e minoria >=10%") & (sensitivity.minimo_comuns == 5)]
    axes[0].plot(cont_sens.limiar, cont_sens.densidade, "o-", label="Minoria ≥10%")
    axes[0].set(title="Sensibilidade ao limiar", xlabel="Limiar de concordância", ylabel="Densidade da rede")
    axes[0].legend()
    active = graph.subgraph([n for n, d in graph.degree if d]).copy()
    if active:
        pos = nx.spring_layout(active, seed=42, iterations=30)
        # Desenhar só uma amostra de arestas; cálculos usam a rede completa.
        edge_list = list(active.edges)
        draw_edges = random.Random(42).sample(edge_list, min(1800, len(edge_list)))
        nx.draw_networkx_edges(active, pos, edgelist=draw_edges, ax=axes[1], alpha=.06, width=.3)
        nx.draw_networkx_nodes(active, pos, ax=axes[1], node_color=[labels.get(n, 0) for n in active],
                               cmap="tab10", node_size=12)
    axes[1].axis("off")
    axes[1].set_title("Comunidades de concordância; layout ilustrativo")
    fig.tight_layout()
    fig.savefig(figures / "02_sensibilidade_e_rede.png", dpi=150)
    plt.close(fig)

    if not composition.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        image = ax.imshow(composition, cmap="Blues", aspect="auto")
        ax.set_yticks(range(len(composition)), composition.index)
        ax.set_xticks(range(len(composition.columns)), [str(x) for x in composition.columns])
        ax.set(xlabel="Comunidade (0 = isolado)", ylabel="Partido observado nos votos", title="Composição das comunidades na amostra")
        fig.colorbar(image, ax=ax, label="Deputados")
        fig.tight_layout()
        fig.savefig(figures / "03_partidos_comunidades.png", dpi=150)
        plt.close(fig)

    timestamps = [x["coletado_em"] for x in data["requisicoes"]]
    summary = {"inicio": data["inicio"], "fim": data["fim"], "data_coleta": min(timestamps),
        "fim_coleta": max(timestamps), "execucao_iniciada_em": data["coleta_iniciada_em"],
        "catalogo": data["catalogo"], "amostragem": data["amostragem"],
        "votacoes_consultadas": len(data["votacoes_consultadas"]),
        "votacoes_com_votos": int(valid.idVotacao.nunique()), "registros_votos": len(votes),
        "deputados_com_votos": int(valid.idDeputado.nunique()), "duplicatas_chave": duplicates,
        "chaves_conflitantes": conflicts, "ids_ausentes": int(votes.idDeputado.isna().sum()),
        "tipos_voto": valid.voto.value_counts().to_dict(), "deputados_com_mais_de_um_partido": party_changes,
        "votacoes_binarias": len(totals), "votacoes_minoria_10pct": len(contested_ids),
        "votacoes_minoria_menos_10pct": int((totals.fracao_minoria < .1).sum()),
        "votos_com_orientacao_direta_comparavel": len(comparable),
        "chaves_orientacao_conflitantes": len(orientation_bad),
        "taxa_adesao_global_na_parcela_comparavel": float(comparable.concorda.mean()) if len(comparable) else None,
        "fracao_votos_binarios_com_orientacao_direta": len(comparable) / len(binary) if len(binary) else 0,
        "proposicoes_enriquecidas": len(data["proposicoes_consultadas"]),
        "proposicoes_com_autores": len(authors_by_prop),
        "proposicoes_com_multiplos_autores": sum(n > 1 for n in authors_by_prop.values()),
        "proposicoes_com_tema": len(themes_by_prop),
        "registros_despesas": len(expenses),
        "deputados_despesas_consultados": len([q for q in data["consultas"] if q["tipo"] == "despesas"]),
        "registros_presenca_eventos": sum(len(q["dados"]) for q in data["consultas"] if q["tipo"] == "presencas"),
        "registros_tramitacoes": len(proceedings),
        "consultas_com_erro": sum(x["status"] == "erro" for x in data["consultas"]),
        "consultas_404": sum(x["status"] == 404 for x in data["consultas"]),
        "requisicoes_na_execucao": len(data["requisicoes"]),
        "consultas_recuperadas_cache": sum(x["cache"] for x in data["requisicoes"]),
        "grafos": graph_rows}
    (out / "resumo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inicio", default="2023-08-01")
    parser.add_argument("--fim", default="2023-08-31")
    parser.add_argument("--limite-votacoes", type=int, default=30)
    parser.add_argument("--limite-proposicoes", type=int, default=12)
    parser.add_argument("--max-requisicoes", type=int, default=200)
    parser.add_argument("--cache", type=Path, default=Path(__file__).parent / "cache_eda")
    parser.add_argument("--saida", type=Path, default=Path(__file__).parent / "resultados_eda")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--so-coleta", action="store_true")
    parser.add_argument("--analisar-coleta", type=Path)
    args = parser.parse_args()
    if args.inicio > args.fim or args.inicio[:4] != args.fim[:4]:
        parser.error("Datas devem formar um intervalo crescente no mesmo ano.")
    if args.limite_votacoes < 1 or args.limite_proposicoes < 1:
        parser.error("Limites devem ser positivos.")
    args.saida.mkdir(parents=True, exist_ok=True)
    if args.analisar_coleta:
        data = json.loads(args.analisar_coleta.read_text(encoding="utf-8"))
    else:
        api = CamaraAPI(args.cache, offline=args.offline, max_requests=args.max_requisicoes)
        data = collect(api, args.inicio, args.fim, args.limite_votacoes, args.limite_proposicoes)
        (args.saida / "coleta.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        pd.DataFrame(api.log).to_csv(args.saida / "manifesto_consultas.csv", index=False)
    if not args.so_coleta:
        summary = analyse(data, args.saida)
        print(json.dumps({k: v for k, v in summary.items() if k not in ("catalogo", "grafos")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
