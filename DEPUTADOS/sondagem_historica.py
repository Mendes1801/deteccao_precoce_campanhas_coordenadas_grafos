"""Sondagem pequena de possibilidades históricas; não é análise de vinte anos."""
from __future__ import annotations

import argparse
import calendar
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from camara_api import CamaraAPI

ANOS_REFERENCIA = [2006, 2011, 2016, 2021, 2025]


def janela_mes(ano, mes):
    return f"{ano}-{mes:02d}-01", f"{ano}-{mes:02d}-{calendar.monthrange(ano, mes)[1]}"


def maior_placar(registros):
    """Prioriza uma resposta com potencial de muitos votos; não sorteio estatístico."""
    def score(item):
        return sum(int(n) for n in re.findall(r"(?:Sim|não)\s*:\s*(\d+)", item.get("descricao") or "", re.I))
    return max(registros, key=score, default=None)


def sondar(api, anos=ANOS_REFERENCIA):
    consultas = []
    def run(job):
        ano, tipo, path, params = job
        try:
            rows, info = api.list(path, params, max_pages=1)
            return {"ano": ano, "tipo": tipo, "rota": path, "filtros": params,
                    "dados": rows, **info}
        except Exception as error:
            return {"ano": ano, "tipo": tipo, "rota": path, "filtros": params,
                    "dados": [], "status": "erro", "completo": False, "erro": str(error)}

    jobs = []
    for ano in anos:
        for mes in (3, 8):
            inicio, fim = janela_mes(ano, mes)
            jobs.append((ano, "catalogo_votacoes", "/votacoes", {
                "dataInicio": inicio, "dataFim": fim, "idOrgao": 180,
                "itens": 50, "ordem": "ASC", "ordenarPor": "dataHoraRegistro"}))
        jobs.append((ano, "catalogo_proposicoes", "/proposicoes", {
            "ano": ano, "siglaTipo": "PL", "itens": 1, "ordem": "ASC", "ordenarPor": "id"}))
    with ThreadPoolExecutor(max_workers=3) as pool:
        consultas.extend(pool.map(run, jobs))
    jobs = []
    selected = {}
    for ano in anos:
        rows = [r for q in consultas if q["ano"] == ano and q["tipo"] == "catalogo_votacoes" for r in q["dados"]]
        chosen = maior_placar(rows)
        props = [r for q in consultas if q["ano"] == ano and q["tipo"] == "catalogo_proposicoes" for r in q["dados"]]
        selected[ano] = {"votacao": chosen, "proposicao": props[0] if props else None}
        if chosen:
            for resource in ("votos", "orientacoes"):
                jobs.append((ano, resource, f"/votacoes/{chosen['id']}/{resource}", None))
        if props:
            for resource in ("autores", "temas"):
                jobs.append((ano, resource, f"/proposicoes/{props[0]['id']}/{resource}", None))
    with ThreadPoolExecutor(max_workers=3) as pool:
        consultas.extend(pool.map(run, jobs))
    summary = []
    for ano in anos:
        year = [q for q in consultas if q["ano"] == ano]
        by_type = lambda kind: [r for q in year if q["tipo"] == kind for r in q["dados"]]
        votes = by_type("votos")
        summary.append({"ano_referencia": ano,
            "metadados_votacoes_inspecionados": len(by_type("catalogo_votacoes")),
            "votacoes_com_votos_inspecionadas": int(bool(votes)),
            "registros_voto_inspecionados": len(votes),
            "votos_com_id_deputado": sum(bool((v.get("deputado_") or {}).get("id")) for v in votes),
            "orientacoes_inspecionadas": len(by_type("orientacoes")),
            "PL_inspecionados": len(by_type("catalogo_proposicoes")),
            "autores_inspecionados": len(by_type("autores")),
            "temas_inspecionados": len(by_type("temas")),
            "consultas_com_falha": sum(q["status"] not in (200,) for q in year),
            "limite": "Março/agosto, até 50 metadados por mês; uma decisão e um PL. Não representa o ano."})
    return {"execucao_em": datetime.now(timezone.utc).isoformat(),
        "horizonte_proposto": {"inicio": "2006-01-01", "fim": "2025-12-31", "anos_civis": 20,
                              "status": "escopo de estudo futuro; cobertura integral não verificada"},
        "anos_amostrados": list(anos), "resumo": summary,
        "selecionados": selected, "consultas": consultas, "manifesto": api.log,
        "metodo": "Sondagem de esquema e presença em cinco momentos. Sem totais anuais, redes históricas, rankings ou inferência de tendência."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(__file__).parent / "cache_eda")
    parser.add_argument("--saida", type=Path, default=Path(__file__).parent / "resultados_viabilidade")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    api = CamaraAPI(args.cache, offline=args.offline, max_requests=50)
    result = sondar(api)
    args.saida.mkdir(parents=True, exist_ok=True)
    # Respostas completas permanecem no cache local, sem grande exportação duplicada.
    slim = {k: v for k, v in result.items() if k not in ("consultas", "selecionados")}
    slim["evidencias"] = [{k: v for k, v in q.items() if k != "dados"} |
                         {"registros_retornados": len(q["dados"]),
                          "campos_observados": sorted(q["dados"][0]) if q["dados"] else []}
                         for q in result["consultas"]]
    (args.saida / "sondagem.json").write_text(json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"resumo": result["resumo"], "consultas": len(api.log),
                      "cache": sum(x["cache"] for x in api.log)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
