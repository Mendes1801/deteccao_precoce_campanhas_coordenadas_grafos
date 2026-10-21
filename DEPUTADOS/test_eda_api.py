"""Verificações das escolhas que poderiam alterar as conclusões do EDA."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from camara_api import CamaraAPI
from eda_api import pair_matrices, make_graph, select_sample


class TestEDA(unittest.TestCase):
    def test_absence_is_not_disagreement(self):
        votes = pd.DataFrame([
            (1, "a", "Sim"), (1, "b", "Não"),
            (2, "a", "Sim"), (2, "c", "Não"),
        ], columns=["idDeputado", "idVotacao", "voto"])
        ids, shared, rates = pair_matrices(votes)
        self.assertEqual(ids, [1, 2])
        self.assertEqual(shared[0, 1], 1)
        self.assertEqual(rates[0, 1], 1.)
        self.assertEqual(make_graph(ids, shared, rates, .7, 2).number_of_edges(), 0)

    def test_conflicting_duplicates_are_excluded(self):
        votes = pd.DataFrame([(1, "a", "Sim"), (1, "a", "Não"), (2, "a", "Sim")],
                             columns=["idDeputado", "idVotacao", "voto"])
        ids, shared, rates = pair_matrices(votes)
        self.assertEqual(ids, [2])

    def test_stable_id_unites_party_changes(self):
        votes = pd.DataFrame([(1, "a", "Sim", "X"), (1, "b", "Sim", "Y"),
                              (2, "a", "Sim", "Y"), (2, "b", "Não", "Y")],
                             columns=["idDeputado", "idVotacao", "voto", "partido"])
        ids, shared, rates = pair_matrices(votes)
        self.assertEqual(len(ids), 2)
        self.assertEqual(rates[0, 1], .5)

    def test_pagination_and_partial_coverage(self):
        api = CamaraAPI(Path(tempfile.mkdtemp()))
        records = [
            {"url": "u1", "status": 200, "payload": {"dados": [{"id": 1}], "links": [{"rel": "next", "href": "u2"}]}},
            {"url": "u2", "status": 200, "payload": {"dados": [{"id": 2}], "links": []}},
        ]
        with patch.object(api, "get", side_effect=records):
            rows, info = api.list("/deputados", max_pages=1)
            self.assertFalse(info["completo"])
            self.assertEqual(len(rows), 1)
        with patch.object(api, "get", side_effect=records):
            rows, info = api.list("/deputados", max_pages=2)
            self.assertTrue(info["completo"])
            self.assertEqual(len(rows), 2)

    def test_404_is_not_empty_success(self):
        api = CamaraAPI(Path(tempfile.mkdtemp()))
        with patch.object(api, "get", return_value={"url": "u", "status": 404, "payload": {}}):
            rows, info = api.list("/votacoes/x/votos")
            self.assertEqual(info["status"], 404)
            self.assertFalse(info["completo"])

    def test_sample_reproducible(self):
        data = [{"id": x} for x in range(100)]
        self.assertEqual(select_sample(data, 10), select_sample(data, 10))


if __name__ == "__main__":
    unittest.main()
