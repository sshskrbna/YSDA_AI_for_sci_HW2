#!/usr/bin/env python3
"""Статистика трёх FASTA для ДЗ 1.

Данные: homework/inputs.tsv — три строки (sample_id, source, ...), где source
указывает на FASTA в homework/data/. Последовательности — пластомы Taraxacum.

Проверка: python3 checks/check_hw1_fasta.py независимо пересчитывает результат
и возвращает 0 при совпадении.

Используется в: results/hw1/fasta_stats.csv (столбцы sample_id, source,
length_bp, a_count, c_count, g_count, t_count, ambiguous_count, gc_percent).
"""

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = os.path.join(ROOT, "homework", "inputs.tsv")
OUTPUT = os.path.join(ROOT, "results", "hw1", "fasta_stats.csv")


def sequence_stats(path):
    """Читает FASTA, возвращает словарь статистики последовательности."""
    seq = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(">"):
                continue
            seq.append(line)
    seq = "".join(seq).upper()

    length = len(seq)
    a = seq.count("A")
    c = seq.count("C")
    g = seq.count("G")
    t = seq.count("T")
    ambiguous = length - (a + c + g + t)
    gc = (g + c) / (a + c + g + t) * 100.0 if (a + c + g + t) else 0.0
    return {
        "length_bp": length,
        "a_count": a,
        "c_count": c,
        "g_count": g,
        "t_count": t,
        "ambiguous_count": ambiguous,
        "gc_percent": gc,
    }


def main():
    rows = []
    with open(INPUTS) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for rec in reader:
            sample_id = rec["sample_id"]
            source = rec["source"]
            stats = sequence_stats(os.path.join(ROOT, source))
            rows.append({
                "sample_id": sample_id,
                "source": source,
                **stats,
            })

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "sample_id", "source", "length_bp", "a_count", "c_count",
                "g_count", "t_count", "ambiguous_count", "gc_percent",
            ],
        )
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["gc_percent"] = f"{row['gc_percent']:.8f}"
            writer.writerow(out)

    print(f"Записано строк: {len(rows)} -> {OUTPUT}")


if __name__ == "__main__":
    main()