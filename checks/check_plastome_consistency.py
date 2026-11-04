#!/usr/bin/env python3
"""Верификатор согласованности координат и длин LSC, SSC, IR у пластомов.

ДЗ 2 «Проверка», вычислительное направление B. Только стандартная библиотека Python 3.

Данные: homework/structure/ir_boundaries.csv (границы и длины областей) и
results/hw1/fasta_stats.csv (полные длины пластомов).

Проверка: свойства 1-7 из METHOD.md. Контроль версии (SHA-256) и проверка содержимого
разделены (раздел 2 METHOD.md): SHA-256 проверяет неизменность оригиналов отдельным шагом;
проверка содержимого выполняется на переданных данных без требования совпадения SHA-256.

Используется в: checks/check_plastome_consistency.py (команда запуска из AGENTS.md),
scripts/hw2_synthetic_and_k4.py (синтетические примеры и эксперимент К4).
"""

import csv
import hashlib
import os
import sys

# Версии оригиналов (SHA-256) — раздел 2.1 METHOD.md.
ORIGINAL_SHA256 = {
    "homework/structure/ir_boundaries.csv":
        "3acff4cd2ce48f0c4ed3803a2d7150b516207f4dbf05f7d7eb28e257a453ccee",
    "results/hw1/fasta_stats.csv":
        "3a309eafc507f200a960fb79bd69f90030ab3b2d30472d3c1a64711911f30329",
}

# Однозначное сопоставление sample_id (без версии) -> accession (с версией).
SAMPLE_MAP = {
    "KU361241": "KU361241.1",
    "KU736960": "KU736960.1",
    "NC_032056": "NC_032056.1",
}

IR_COLUMNS = [
    "sample_id", "ir1_start", "ir1_end", "ir2_start", "ir2_end", "ir_bp",
    "ir_copy_length_difference", "lsc_bp", "ssc_bp", "ir_identity_percent",
]
STATS_COLUMNS = [
    "sample_id", "source", "length_bp", "a_count", "c_count", "g_count",
    "t_count", "ambiguous_count", "gc_percent",
]
INT_COLS_IR = [
    "ir1_start", "ir1_end", "ir2_start", "ir2_end", "ir_bp",
    "ir_copy_length_difference", "lsc_bp", "ssc_bp",
]
INT_COLS_STATS = ["length_bp"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_version(ir_path, stats_path):
    """Контроль версии оригиналов (SHA-256). Возвращает список нарушений."""
    violations = []
    for path, expected in ORIGINAL_SHA256.items():
        if not os.path.exists(path):
            violations.append(f"версия: файл не найден: {path}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            violations.append(
                f"версия: SHA-256 {path} не совпадает с оригиналом "
                f"(ожидалось {expected}, получено {actual})")
    return violations


def _read_csv(path, required_cols):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return None, ["схема: пустой файл"]
        missing = [c for c in required_cols if c not in reader.fieldnames]
        if missing:
            return None, [f"схема: отсутствуют столбцы: {', '.join(missing)}"]
        rows = list(reader)
    return rows, []


def _to_int(value, col, row_id, violations):
    try:
        return int(value)
    except (TypeError, ValueError):
        violations.append(
            f"тип: {row_id}: столбец {col} не целое число: {value!r}")
        return None


def verify_content(ir_path, stats_path, simple=False):
    """Проверка содержимого. Возвращает список нарушений.

    simple=True — только свойства 1-2 (схема, типы, наборы образцов, порядок координат);
    simple=False — все свойства 1-7. Не требует совпадения SHA-256 с оригиналом
    (раздел 2.2 METHOD.md).
    """
    violations = []

    # --- Свойство 1: полнота схемы, типы, наборы образцов, дубликаты ---
    ir_rows, errs = _read_csv(ir_path, IR_COLUMNS)
    if errs:
        return errs
    stats_rows, errs = _read_csv(stats_path, STATS_COLUMNS)
    if errs:
        return errs

    # Типы.
    for row in ir_rows:
        rid = row["sample_id"]
        for col in INT_COLS_IR:
            _to_int(row[col], col, rid, violations)
    for row in stats_rows:
        rid = row["sample_id"]
        _to_int(row["length_bp"], "length_bp", rid, violations)

    # Наборы образцов и дубликаты.
    ir_ids = [r["sample_id"] for r in ir_rows]
    stats_ids = [r["sample_id"] for r in stats_rows]
    if len(ir_ids) != len(set(ir_ids)):
        violations.append("схема: дубликаты sample_id в ir_boundaries.csv")
    if len(stats_ids) != len(set(stats_ids)):
        violations.append("схема: дубликаты sample_id в fasta_stats.csv")
    unknown = [i for i in ir_ids if i not in SAMPLE_MAP]
    if unknown:
        violations.append(f"схема: неизвестные sample_id в ir_boundaries.csv: {unknown}")
    unknown_s = [i for i in stats_ids if i not in SAMPLE_MAP.values()]
    if unknown_s:
        violations.append(f"схема: неизвестные sample_id в fasta_stats.csv: {unknown_s}")
    expected_ir = set(SAMPLE_MAP.keys())
    expected_stats = set(SAMPLE_MAP.values())
    if set(ir_ids) != expected_ir:
        violations.append(
            f"схема: набор образцов ir_boundaries.csv не совпадает с ожидаемым "
            f"(получено {sorted(set(ir_ids))}, ожидалось {sorted(expected_ir)})")
    if set(stats_ids) != expected_stats:
        violations.append(
            f"схема: набор образцов fasta_stats.csv не совпадает с ожидаемым "
            f"(получено {sorted(set(stats_ids))}, ожидалось {sorted(expected_stats)})")

    # Если схема нарушена, дальше проверять нечего.
    if violations:
        return violations

    # Сопоставление и сбор данных.
    stats_by_id = {r["sample_id"]: r for r in stats_rows}
    for row in ir_rows:
        sid = row["sample_id"]
        acc = SAMPLE_MAP[sid]
        if acc not in stats_by_id:
            violations.append(f"схема: нет строки {acc} в fasta_stats.csv")
            continue
        ir = {c: int(row[c]) for c in INT_COLS_IR}
        length = int(stats_by_id[acc]["length_bp"])
        ir1_start, ir1_end = ir["ir1_start"], ir["ir1_end"]
        ir2_start, ir2_end = ir["ir2_start"], ir["ir2_end"]
        ir_bp = ir["ir_bp"]
        diff = ir["ir_copy_length_difference"]
        lsc_bp, ssc_bp = ir["lsc_bp"], ir["ssc_bp"]

        ir1_len = ir1_end - ir1_start + 1
        ir2_len = ir2_end - ir2_start + 1

        # --- Свойство 2: порядок координат ---
        if not (1 < ir1_start <= ir1_end < ir2_start <= ir2_end == length):
            violations.append(
                f"свойство 2: {acc}: нарушен порядок координат "
                f"(1 < {ir1_start} <= {ir1_end} < {ir2_start} <= {ir2_end} = {length})")

        if simple:
            continue

        # --- Свойство 3: lsc_bp = ir1_start - 1 ---
        if lsc_bp != ir1_start - 1:
            violations.append(
                f"свойство 3: {acc}: lsc_bp={lsc_bp} != ir1_start-1={ir1_start - 1}")

        # --- Свойство 4: IR1_length и ir_bp ---
        if ir1_len != ir_bp:
            violations.append(
                f"свойство 4: {acc}: IR1_length={ir1_len} != ir_bp={ir_bp}")

        # --- Свойство 5: ssc_bp = ir2_start - ir1_end - 1 ---
        if ssc_bp != ir2_start - ir1_end - 1:
            violations.append(
                f"свойство 5: {acc}: ssc_bp={ssc_bp} != ir2_start-ir1_end-1="
                f"{ir2_start - ir1_end - 1}")

        # --- Свойство 6: IR2_length и разность IR ---
        if diff == 0:
            if ir1_len != ir2_len:
                violations.append(
                    f"свойство 6: {acc}: IR1_length={ir1_len} != IR2_length={ir2_len} "
                    f"при ir_copy_length_difference=0")
        else:
            violations.append(
                f"свойство 6: {acc}: ir_copy_length_difference={diff} != 0 — "
                f"семантика поля не определена, проверка не завершена")

        # --- Свойство 7: сумма длин = length_bp ---
        total = lsc_bp + ir1_len + ssc_bp + ir2_len
        if total != length:
            violations.append(
                f"свойство 7: {acc}: lsc+IR1+ssc+IR2={total} != length_bp={length}")

    return violations


def main(argv):
    ir_path = "homework/structure/ir_boundaries.csv"
    stats_path = "results/hw1/fasta_stats.csv"
    no_version = False
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--ir":
            ir_path = args.pop(0)
        elif a == "--stats":
            stats_path = args.pop(0)
        elif a == "--no-version-check":
            no_version = True
        else:
            print(f"неизвестный аргумент: {a}", file=sys.stderr)
            return 2

    violations = []
    if not no_version:
        # Контроль версии оригиналов — отдельный шаг (раздел 2.1).
        violations += check_version(ir_path, stats_path)
        if violations:
            print("КОНТРОЛЬ ВЕРСИИ: НЕ ПРОЙДЕН")
            for v in violations:
                print("  -", v)
            return 1

    # Проверка содержимого (раздел 2.2).
    violations = verify_content(ir_path, stats_path)
    if violations:
        print("ПРОВЕРКА СОДЕРЖИМОГО: НЕ ПРОЙДЕНА")
        for v in violations:
            print("  -", v)
        return 1
    print("OK: все свойства 1-7 выполнены")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))