"""Exporta votações e votos nominais da Câmara em arquivos JSON Lines."""

from __future__ import annotations

import argparse
import calendar
import json
from pathlib import Path
from typing import Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
PASTA_DADOS = Path(__file__).resolve().parent / "dados"


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
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json"})
    return session


def iterar_itens(
    session: requests.Session, url: str, params: dict | None = None
) -> Iterator[dict]:
    while url:
        resposta = session.get(url, params=params, timeout=30)
        resposta.raise_for_status()
        payload = resposta.json()
        yield from payload.get("dados", [])
        url = next(
            (
                link["href"]
                for link in payload.get("links", [])
                if link.get("rel") == "next"
            ),
            "",
        )
        params = None


def meses_do_ano(ano: int) -> Iterator[tuple[str, str]]:
    for mes in range(1, 13):
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        yield f"{ano}-{mes:02d}-01", f"{ano}-{mes:02d}-{ultimo_dia:02d}"


def exportar(ano: int, pasta_saida: Path) -> tuple[int, int]:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_votacoes = pasta_saida / f"votacoes_{ano}.jsonl"
    caminho_votos = pasta_saida / f"votos_nominais_{ano}.jsonl"
    temporario_votacoes = caminho_votacoes.with_suffix(".jsonl.tmp")
    temporario_votos = caminho_votos.with_suffix(".jsonl.tmp")
    quantidade_votacoes = 0
    quantidade_votos = 0
    votacoes_sem_votos_nominais = 0

    with (
        criar_sessao() as session,
        temporario_votacoes.open("w", encoding="utf-8") as arquivo_votacoes,
        temporario_votos.open("w", encoding="utf-8") as arquivo_votos,
    ):
        for data_inicio, data_fim in meses_do_ano(ano):
            print(f"Consultando votações de {data_inicio} a {data_fim}...")
            url = f"{API_BASE}/votacoes"
            params = {
                "dataInicio": data_inicio,
                "dataFim": data_fim,
                "ordem": "ASC",
                "ordenarPor": "dataHoraRegistro",
                "itens": 100,
            }

            for votacao in iterar_itens(session, url, params):
                id_votacao = votacao["id"]
                arquivo_votacoes.write(
                    json.dumps(votacao, ensure_ascii=False) + "\n"
                )
                quantidade_votacoes += 1

                votos_url = f"{API_BASE}/votacoes/{id_votacao}/votos"
                try:
                    for voto in iterar_itens(session, votos_url):
                        registro = {**voto, "idVotacao": id_votacao}
                        arquivo_votos.write(
                            json.dumps(registro, ensure_ascii=False) + "\n"
                        )
                        quantidade_votos += 1
                except requests.HTTPError as erro:
                    if (
                        erro.response is None
                        or erro.response.status_code != 404
                        or erro.response.url != votos_url
                    ):
                        raise
                    votacoes_sem_votos_nominais += 1
                    print(
                        f"API retornou 404 para os votos nominais da votação "
                        f"{id_votacao}; metadados mantidos."
                    )

                if quantidade_votacoes % 100 == 0:
                    arquivo_votacoes.flush()
                    arquivo_votos.flush()
                    print(
                        f"Votações exportadas: {quantidade_votacoes}; "
                        f"votos nominais: {quantidade_votos}"
                    )

            arquivo_votacoes.flush()
            arquivo_votos.flush()

    temporario_votacoes.replace(caminho_votacoes)
    temporario_votos.replace(caminho_votos)
    print(
        f"Exportação concluída: {quantidade_votacoes} votações e "
        f"{quantidade_votos} votos nominais; "
        f"{votacoes_sem_votos_nominais} votações sem endpoint nominal."
    )
    print(f"Votações: {caminho_votacoes}")
    print(f"Votos: {caminho_votos}")
    return quantidade_votacoes, quantidade_votos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ano",
        type=int,
        default=2026,
        help="Ano a exportar (padrão: 2026).",
    )
    parser.add_argument(
        "--pasta-saida",
        type=Path,
        default=PASTA_DADOS,
        help="Pasta onde serão salvos os arquivos JSON Lines.",
    )
    args = parser.parse_args()
    exportar(args.ano, args.pasta_saida)


if __name__ == "__main__":
    main()
