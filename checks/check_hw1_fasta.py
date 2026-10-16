#!/usr/bin/env python3
"""Независимая проверка статистики FASTA (ДЗ 1).

Источник данных: homework/inputs.tsv (sample_id, source, original_source, sha256).
Что делает:
  1. Для каждой строки манифеста сверяет SHA-256 файлов source и original_source
     со значением sha256.
  2. Самостоятельно разбирает каждый FASTA (заголовок '>', остальное —
     последовательность, регистр не важен) и считает length_bp, a_count,
     c_count, g_count, t_count, ambiguous_count, gc_percent.
  3. Читает results/hw1/fasta_stats.csv (или путь из --result), требует
     столбцы ровно в порядке sample_id,source,length_bp,a_count,c_count,
     g_count,t_count,ambiguous_count,gc_percent и ровно три строки с
     sample_id из манифеста. Целые — точно, gc_percent — с допуском 1e-6.
  4. Всё совпало — печатает строку с OK, код 0. Иначе — список расхождений,
     код 1. Нет файла результата — сообщение, код 1.

Используется только стандартная библиотека Python 3.
"""

import argparse
import csv
import hashlib
import os
import sys

# Порядок столбцов результата, требуемый заданием.
RESULT_COLUMNS = [
    "sample_id", "source", "length_bp", "a_count", "c_count",
    "g_count", "t_count", "ambiguous_count", "gc_percent",
]

# Символы, считающиеся каноническими нуклеотидами (регистр не важен).
CANONICAL = set("ACGT")


def sha256_file(path):
    """SHA-256 файла в hex."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_fasta(path):
    """Разбирает FASTA: возвращает (length_bp, a, c, g, t, ambiguous, gc_percent).

    Строка заголовка начинается с '>', остальные строки — последовательность.
    Регистр не важен. ambiguous — все символы, кроме A/C/G/T.
    gc_percent = 100*(G+C)/(A+C+G+T).
    """
    a = c = g = t = amb = 0
    in_seq = False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                in_seq = True
                continue
            if not in_seq:
                # Строка до первого заголовка — не последовательность.
                continue
            for ch in line.upper():
                if ch == "A":
                    a += 1
                elif ch == "C":
                    c += 1
                elif ch == "G":
                    g += 1
                elif ch == "T":
                    t += 1
                else:
                    amb += 1
    length_bp = a + c + g + t
    denom = a + c + g + t
    gc_percent = 100.0 * (g + c) / denom if denom else 0.0
    return length_bp, a, c, g, t, amb, gc_percent


def read_manifest(path):
    """Читает homework/inputs.tsv -> список dict."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def read_result(path):
    """Читает CSV результата -> (headers, rows)."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--result",
        default="results/hw1/fasta_stats.csv",
        help="путь к CSV результата (по умолчанию results/hw1/fasta_stats.csv)",
    )
    ap.add_argument(
        "--manifest",
        default="homework/inputs.tsv",
        help="путь к манифесту (по умолчанию homework/inputs.tsv)",
    )
    args = ap.parse_args()

    problems = []

    # 1. Манифест.
    if not os.path.exists(args.manifest):
        print(f"Нет файла манифеста: {args.manifest}")
        return 1
    manifest = read_manifest(args.manifest)
    if not manifest:
        print("Манифест пуст.")
        return 1

    # 2. Сверка SHA-256 source и original_source.
    for row in manifest:
        sid = row.get("sample_id", "")
        expected = row.get("sha256", "").strip().lower()
        for key in ("source", "original_source"):
            path = row.get(key, "")
            if not path:
                problems.append(f"{sid}: отсутствует путь {key}")
                continue
            if not os.path.exists(path):
                problems.append(f"{sid}: нет файла {key} -> {path}")
                continue
            actual = sha256_file(path)
            if actual != expected:
                problems.append(
                    f"{sid}: SHA-256 {key} не совпадает "
                    f"(ожидалось {expected}, получено {actual})"
                )

    # 3. Самостоятельный расчёт статистики по FASTA.
    expected_stats = {}
    for row in manifest:
        sid = row.get("sample_id", "")
        path = row.get("source", "")
        if not path or not os.path.exists(path):
            if path:
                problems.append(f"{sid}: нет файла source для расчёта -> {path}")
            continue
        length_bp, a, c, g, t, amb, gc = parse_fasta(path)
        expected_stats[sid] = {
            "length_bp": length_bp,
            "a_count": a,
            "c_count": c,
            "g_count": g,
            "t_count": t,
            "ambiguous_count": amb,
            "gc_percent": gc,
        }

    # 4. Чтение результата.
    if not os.path.exists(args.result):
        print(f"Нет файла результата: {args.result}")
        return 1
    headers, rows = read_result(args.result)

    if headers != RESULT_COLUMNS:
        problems.append(
            f"Столбцы результата не совпадают: ожидалось {RESULT_COLUMNS}, "
            f"получено {headers}"
        )

    # Сопоставление строк результата по sample_id.
    result_by_id = {}
    for r in rows:
        if not r:
            continue
        d = dict(zip(headers, r))
        result_by_id[d.get("sample_id", "")] = d

    manifest_ids = [row.get("sample_id", "") for row in manifest]
    if len(result_by_id) != len(manifest_ids):
        problems.append(
            f"Число строк результата ({len(result_by_id)}) не равно числу "
            f"образцов в манифесте ({len(manifest_ids)})"
        )

    # 5. Сверка значений.
    for sid in manifest_ids:
        if sid not in expected_stats:
            continue
        exp = expected_stats[sid]
        if sid not in result_by_id:
            problems.append(f"{sid}: нет строки в результате")
            continue
        got = result_by_id[sid]
        for col in ("length_bp", "a_count", "c_count", "g_count", "t_count",
                    "ambiguous_count"):
            try:
                gv = int(got.get(col, ""))
            except (TypeError, ValueError):
                problems.append(f"{sid}: {col} не целое число: {got.get(col)!r}")
                continue
            if gv != exp[col]:
                problems.append(
                    f"{sid}: {col} не совпадает (ожидалось {exp[col]}, "
                    f"получено {gv})"
                )
        # gc_percent с допуском 1e-6.
        try:
            gg = float(got.get("gc_percent", ""))
        except (TypeError, ValueError):
            problems.append(f"{sid}: gc_percent не число: {got.get('gc_percent')!r}")
            continue
        if abs(gg - exp["gc_percent"]) > 1e-6:
            problems.append(
                f"{sid}: gc_percent не совпадает (ожидалось "
                f"{exp['gc_percent']:.9f}, получено {gg:.9f})"
            )

    if problems:
        print("FAIL")
        for p in problems:
            print("  - " + p)
        return 1

    print("OK: все проверки пройдены")
    return 0


if __name__ == "__main__":
    sys.exit(main())