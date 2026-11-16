# Integrantes: Camila Nunes Carniel (RA/e-mail pendentes); Bruno Germanetti (RA/e-mail pendentes).
# Conteúdo: testes de exclusões e exportação CSV da tabela de atributos parciais.
# Histórico de alterações:
# 11/11/2026 | Grupo | Inclusão de identificação, síntese e histórico para a entrega N2.

import csv

from len_eda.pipeline import load_exclusions, write_feature_table


def test_load_exclusions_reads_only_marked_rows(tmp_path):
    path = tmp_path / "exclusions.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "exclude", "reason"])
        writer.writeheader()
        writer.writerow({"file": "a.json", "exclude": "true", "reason": "duplicate"})
        writer.writerow({"file": "b.json", "exclude": "false", "reason": "keep"})
    assert load_exclusions(path) == {"a.json"}


def test_write_feature_table_quotes_hashtag_topics(tmp_path):
    output = tmp_path / "features.csv"
    write_feature_table(
        [{"file": "#topic.json", "topic": "#topic", "fraction": 0.1}],
        output,
    )

    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[1].startswith('"#topic.json","#topic",')
