"""Cliente de leitura da API: limites explícitos, cache auditável e paginação."""
from __future__ import annotations

import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://dadosabertos.camara.leg.br/api/v2"


class CamaraAPI:
    def __init__(self, cache: Path, offline: bool = False, max_requests: int = 200):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.offline = offline
        self.max_requests = max_requests
        self.log: list[dict] = []
        self._local = threading.local()
        self._lock = threading.Lock()
        self._requests = 0

    def _session(self):
        if not hasattr(self._local, "session"):
            session = requests.Session()
            session.headers.update({"Accept": "application/json", "User-Agent": "TCC-EDA-Camara/1.0"})
            retry = Retry(total=2, backoff_factor=0.5,
                          status_forcelist=(429, 500, 502, 503, 504),
                          allowed_methods={"GET"}, respect_retry_after_header=True)
            session.mount("https://", HTTPAdapter(max_retries=retry))
            self._local.session = session
        return self._local.session

    def get(self, path: str, params: dict | None = None) -> dict:
        url = path if path.startswith("https://") else BASE + "/" + path.lstrip("/")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "dadosabertos.camara.leg.br" or not parsed.path.startswith("/api/v2/"):
            raise ValueError("Apenas URLs da API oficial são aceitas.")
        if params:
            url += ("&" if "?" in url else "?") + urlencode(sorted(params.items()), doseq=True)
        key = hashlib.sha256(url.encode()).hexdigest()
        file = self.cache / f"{key}.json"
        started = time.monotonic()
        if file.exists():
            record = json.loads(file.read_text(encoding="utf-8"))
            cached = True
        else:
            if self.offline:
                raise FileNotFoundError(f"Consulta ausente do cache: {url}")
            with self._lock:
                if self._requests >= self.max_requests:
                    raise RuntimeError("Limite de requisições atingido; reduza a amostra ou aumente --max-requisicoes.")
                self._requests += 1
            response = self._session().get(url, timeout=(10, 30))
            # 404 é uma observação de indisponibilidade, nunca uma lista vazia silenciosa.
            if response.status_code not in (200, 404):
                response.raise_for_status()
            try:
                payload = response.json()
            except ValueError:
                payload = {"erro": response.text[:200]}
            record = {"url": url, "status": response.status_code,
                      "coletado_em": datetime.now(timezone.utc).isoformat(), "payload": payload}
            temp = file.with_suffix(f".{threading.get_ident()}.tmp")
            temp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            temp.replace(file)
            cached = False
        with self._lock:
            self.log.append({"url": url, "status": record["status"], "cache": cached,
                             "coletado_em": record["coletado_em"],
                             "segundos": round(time.monotonic() - started, 3)})
        return record

    def list(self, path: str, params: dict | None = None, max_pages: int = 1) -> tuple[list, dict]:
        records, visited = [], set()
        next_url, next_params = path, params
        status, pages = None, 0
        while next_url and pages < max_pages:
            record = self.get(next_url, next_params)
            if record["url"] in visited:
                raise RuntimeError("Link de paginação repetido pela API.")
            visited.add(record["url"])
            pages += 1
            status = record["status"]
            if status == 404:
                return records, {"status": 404, "paginas": pages, "completo": False, "proxima": None}
            payload = record["payload"]
            data = payload.get("dados")
            if not isinstance(data, list):
                raise ValueError(f"Resposta não é uma listagem: {record['url']}")
            records.extend(data)
            next_url = next((x["href"] for x in payload.get("links", []) if x.get("rel") == "next"), None)
            next_params = None
        return records, {"status": status, "paginas": pages,
                         "completo": next_url is None, "proxima": next_url}
