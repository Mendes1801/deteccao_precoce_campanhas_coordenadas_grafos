import csv

from len_eda.pipeline import load_exclusions


def test_load_exclusions_reads_only_marked_rows(tmp_path):
    path = tmp_path / "exclusions.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "exclude", "reason"])
        writer.writeheader()
        writer.writerow({"file": "a.json", "exclude": "true", "reason": "duplicate"})
        writer.writerow({"file": "b.json", "exclude": "false", "reason": "keep"})
    assert load_exclusions(path) == {"a.json"}
