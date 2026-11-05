#!/usr/bin/env python3
"""Синтетические проверки и эксперимент К4 для верификатора пластома.

ДЗ 2 «Проверка», вычислительное направление B. Только стандартная библиотека Python 3.

Данные: homework/structure/ir_boundaries.csv и results/hw1/fasta_stats.csv (оригиналы,
не изменяются). Синтетические и повреждённые копии создаются во временной папке и
проверяются по содержимому (без требования совпадения SHA-256 с оригиналом).

Используется в: scripts/hw2_synthetic_and_k4.py (команда запуска из AGENTS.md).

Результаты в results/hw2/: synthetic_examples.txt, k4_experiment.csv, k4_summary.txt.
"""

import csv
import os
import random
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "checks"))
from check_plastome_consistency import (  # noqa: E402
    SAMPLE_MAP, verify_content,
)

IR_HEADER = [
    "sample_id", "ir1_start", "ir1_end", "ir2_start", "ir2_end", "ir_bp",
    "ir_copy_length_difference", "lsc_bp", "ssc_bp", "ir_identity_percent",
]
STATS_HEADER = [
    "sample_id", "source", "length_bp", "a_count", "c_count", "g_count",
    "t_count", "ambiguous_count", "gc_percent",
]

# Исходные данные читаются из CSV (не прописываются вручную).
IR_SRC = "homework/structure/ir_boundaries.csv"
STATS_SRC = "results/hw1/fasta_stats.csv"


def read_source_csv(path, header):
    """Читает исходный CSV в список строк (значения как в файле)."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [[row[c] for c in header] for row in reader]


IR_INT_COLS = {1, 2, 3, 4, 5, 6, 7, 8}  # ir1_start..ssc_bp (индексы в IR_HEADER)
STATS_INT_COLS = {2}  # length_bp (индекс в STATS_HEADER)


def load_orig():
    """Возвращает (ORIG_IR, ORIG_STATS) из исходных CSV, числовые столбцы — int."""
    ir = read_source_csv(IR_SRC, IR_HEADER)
    stats = read_source_csv(STATS_SRC, STATS_HEADER)
    for row in ir:
        for i in IR_INT_COLS:
            row[i] = int(row[i])
    for row in stats:
        for i in STATS_INT_COLS:
            row[i] = int(row[i])
    return ir, stats


SEEDS = [1, 2, 3, 4, 5]
COPIES_PER_SEED = 100
BOOTSTRAP_SEED = 42
BOOTSTRAP_N = 1000
PRACTICAL_THRESHOLD = 0.10  # 10 процентных пунктов


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def deep_copy(rows):
    return [list(r) for r in rows]


def run_checks(ir_path, stats_path):
    """Возвращает (full_detected, simple_detected) — обнаружено ли нарушение."""
    full = verify_content(ir_path, stats_path, simple=False)
    simple = verify_content(ir_path, stats_path, simple=True)
    return (len(full) > 0, len(simple) > 0)


# ---------------------------------------------------------------------------
# Синтетические примеры
# ---------------------------------------------------------------------------

def _full_ir(ir1s, ir1e, ir2s, ir2e, ir_bp, diff, lsc, ssc):
    """Полный набор ir_boundaries из 3 образцов; первый (KU361241) — заданный."""
    return [
        ["KU361241", ir1s, ir1e, ir2s, ir2e, ir_bp, diff, lsc, ssc, 100.0],
        ["KU736960", 83923, 108361, 126869, 151307, 24439, 0, 83922, 18507, 100.0],
        ["NC_032056", 83863, 108283, 126862, 151282, 24421, 0, 83862, 18578, 99.996],
    ]


def _full_stats(length):
    """Полный набор fasta_stats из 3 образцов; длина KU361241.1 — заданная."""
    return [
        ["KU361241.1", "src", length, 0, 0, 0, 0, 0, 0.0],
        ["KU736960.1", "src", 151307, 0, 0, 0, 0, 0, 0.0],
        ["NC_032056.1", "src", 151282, 0, 0, 0, 0, 0, 0.0],
    ]


def synthetic_examples(tmpdir):
    """Проверяет положительные и отрицательные синтетические примеры.

    Каждый пример — полный набор из 3 образцов (свойство 1 требует совпадения
    наборов образцов). Возвращает (строки отчёта, all_ok).
    """
    cases = [
        # (имя, ir_rows, stats_rows, ожидаемый код, ожидаемое свойство или None)
        ("positive_normal_4regions",
         _full_ir(11, 20, 31, 40, 10, 0, 10, 10), _full_stats(40), 0, None),
        ("positive_ssc0_technical",
         _full_ir(2, 2, 3, 3, 1, 0, 1, 0), _full_stats(3), 0, None),
        ("neg_ir1_start_1",
         _full_ir(1, 20, 31, 40, 10, 0, 0, 10), _full_stats(40), 1, "свойство 2"),
        ("neg_ir1_end_eq_ir2_start_ssc_mismatch",
         _full_ir(11, 20, 21, 40, 10, 0, 10, 10), _full_stats(40), 1, "свойство 5"),
        ("neg_ir2_end_ne_length",
         _full_ir(11, 20, 31, 39, 10, 0, 10, 10), _full_stats(40), 1, "свойство 2"),
        ("neg_lsc_mismatch",
         _full_ir(11, 20, 31, 40, 10, 0, 9, 10), _full_stats(40), 1, "свойство 3"),
        ("neg_ir_bp_mismatch",
         _full_ir(11, 20, 31, 40, 9, 0, 10, 10), _full_stats(40), 1, "свойство 4"),
        ("neg_ssc_mismatch",
         _full_ir(11, 20, 31, 40, 10, 0, 10, 9), _full_stats(40), 1, "свойство 5"),
        ("neg_ir_lengths_differ_diff0",
         _full_ir(11, 20, 31, 41, 10, 0, 10, 10), _full_stats(41), 1, "свойство 6"),
        ("neg_nonzero_diff",
         _full_ir(11, 20, 31, 40, 10, 1, 10, 10), _full_stats(40), 1, "свойство 6"),
        ("neg_sum_ne_length",
         _full_ir(11, 20, 31, 40, 10, 0, 10, 11), _full_stats(40), 1, "свойство 7"),
        ("neg_unknown_id",
         [["UNKNOWN", 11, 20, 31, 40, 10, 0, 10, 10, 100.0],
          ["KU736960", 83923, 108361, 126869, 151307, 24439, 0, 83922, 18507, 100.0],
          ["NC_032056", 83863, 108283, 126862, 151282, 24421, 0, 83862, 18578, 99.996]],
         _full_stats(40), 1, "свойство 1"),
        ("neg_duplicate",
         _full_ir(11, 20, 31, 40, 10, 0, 10, 10) + [["KU361241", 11, 20, 31, 40, 10, 0, 10, 10, 100.0]],
         _full_stats(40), 1, "свойство 1"),
    ]

    lines = []
    all_ok = True
    for name, ir_rows, stats_rows, expected_code, expected_prop in cases:
        ir_path = os.path.join(tmpdir, f"{name}_ir.csv")
        stats_path = os.path.join(tmpdir, f"{name}_stats.csv")
        write_csv(ir_path, IR_HEADER, ir_rows)
        write_csv(stats_path, STATS_HEADER, stats_rows)
        violations = verify_content(ir_path, stats_path, simple=False)
        code = 0 if not violations else 1
        ok = (code == expected_code)
        if ok and expected_prop is not None:
            # Проверяем, что нарушение относится к ожидаемому свойству.
            # Свойство 1 (схема/типы) сообщается префиксами "схема:"/"тип:".
            if expected_prop == "свойство 1":
                ok = any(("схема" in v or "тип" in v) for v in violations)
            else:
                ok = any(expected_prop in v for v in violations)
        if not ok:
            all_ok = False
        lines.append(
            f"{name}: код={code} (ожидалось {expected_code}), "
            f"нарушений={len(violations)}"
            + (f", первое: {violations[0]}" if violations else "")
            + (" — OK" if ok else " — НЕВЕРНО"))
    return lines, all_ok


# ---------------------------------------------------------------------------
# Эксперимент К4
# ---------------------------------------------------------------------------

def apply_damage(ir_rows, stats_rows, damage_type, rng):
    """Применяет один тип повреждения к случайному образцу. Возвращает копии."""
    ir = deep_copy(ir_rows)
    stats = deep_copy(stats_rows)
    idx = rng.randrange(len(ir))
    acc = SAMPLE_MAP[ir[idx][0]]
    s_idx = next(i for i, r in enumerate(stats) if r[0] == acc)
    delta = rng.choice([-1, 1])

    if damage_type == "coord":  # (а) сдвиг координаты на ±1
        col = rng.choice([1, 2, 3, 4])  # ir1_start, ir1_end, ir2_start, ir2_end
        ir[idx][col] += delta
    elif damage_type == "lsc":  # (б) изменение lsc_bp на ±1
        ir[idx][7] += delta
    elif damage_type == "ssc":  # (в) изменение ssc_bp на ±1
        ir[idx][8] += delta
    elif damage_type == "ir_bp":  # (г) изменение ir_bp на ±1
        ir[idx][5] += delta
    elif damage_type == "length":  # (д) изменение length_bp на ±1
        stats[s_idx][2] += delta
    else:
        raise ValueError(f"неизвестный тип повреждения: {damage_type}")
    return ir, stats


def run_k4(tmpdir):
    """Эксперимент К4. Возвращает (строки отчёта, all_ok)."""
    ORIG_IR, ORIG_STATS = load_orig()
    damage_types = ["coord", "lsc", "ssc", "ir_bp", "length"]
    rows_out = []  # (seed, copy, type, full_detected, simple_detected, is_control)
    full_det = {s: 0 for s in SEEDS}
    simple_det = {s: 0 for s in SEEDS}
    full_fp = {s: 0 for s in SEEDS}
    simple_fp = {s: 0 for s in SEEDS}
    pairs = []  # (full_detected, simple_detected) на повреждённых копиях

    for seed in SEEDS:
        rng = random.Random(seed)
        # Повреждённые копии: 100, сбалансированные по 5 типам (по 20).
        for copy_no in range(COPIES_PER_SEED):
            dtype = damage_types[copy_no % len(damage_types)]
            ir, stats = apply_damage(ORIG_IR, ORIG_STATS, dtype, rng)
            ir_path = os.path.join(tmpdir, f"k4_{seed}_{copy_no}_ir.csv")
            stats_path = os.path.join(tmpdir, f"k4_{seed}_{copy_no}_stats.csv")
            write_csv(ir_path, IR_HEADER, ir)
            write_csv(stats_path, STATS_HEADER, stats)
            full_d, simple_d = run_checks(ir_path, stats_path)
            full_det[seed] += int(full_d)
            simple_det[seed] += int(simple_d)
            pairs.append((int(full_d), int(simple_d)))
            rows_out.append([seed, copy_no, dtype, int(full_d), int(simple_d), 0])
        # Корректные контроли: 100 без повреждений (повторения одной исходной таблицы).
        for copy_no in range(COPIES_PER_SEED):
            ir_path = os.path.join(tmpdir, f"k4c_{seed}_{copy_no}_ir.csv")
            stats_path = os.path.join(tmpdir, f"k4c_{seed}_{copy_no}_stats.csv")
            write_csv(ir_path, IR_HEADER, ORIG_IR)
            write_csv(stats_path, STATS_HEADER, ORIG_STATS)
            full_d, simple_d = run_checks(ir_path, stats_path)
            full_fp[seed] += int(full_d)
            simple_fp[seed] += int(simple_d)
            rows_out.append([seed, copy_no, "control", int(full_d), int(simple_d), 1])

    # Метрики.
    n_damaged = COPIES_PER_SEED * len(SEEDS)
    n_control = n_damaged
    full_det_rate = sum(full_det.values()) / n_damaged
    simple_det_rate = sum(simple_det.values()) / n_damaged
    full_fp_rate = sum(full_fp.values()) / n_control
    simple_fp_rate = sum(simple_fp.values()) / n_control

    # Парный bootstrap для разности (полная − простая) на повреждённых копиях.
    brng = random.Random(BOOTSTRAP_SEED)
    diffs = [f - s for f, s in pairs]
    boot_means = []
    for _ in range(BOOTSTRAP_N):
        sample = [diffs[brng.randrange(len(diffs))] for _ in range(len(diffs))]
        boot_means.append(sum(sample) / len(sample))
    boot_means.sort()
    lo = boot_means[int(0.025 * BOOTSTRAP_N)]
    hi = boot_means[int(0.975 * BOOTSTRAP_N) - 1]
    mean_diff = sum(diffs) / len(diffs)

    # Вывод по правилу принятия.
    stat_adv = lo > 0.0
    pract_adv = mean_diff >= PRACTICAL_THRESHOLD
    full_all_detected = full_det_rate == 1.0
    no_fp = (full_fp_rate == 0.0 and simple_fp_rate == 0.0)

    # Разброс по seed (доля обнаружения полной проверкой на 100 копий каждого seed).
    per_seed_full = {s: full_det[s] / COPIES_PER_SEED for s in SEEDS}
    per_seed_simple = {s: simple_det[s] / COPIES_PER_SEED for s in SEEDS}
    spread_full = max(per_seed_full.values()) - min(per_seed_full.values())
    spread_simple = max(per_seed_simple.values()) - min(per_seed_simple.values())

    lines = []
    lines.append(f"повреждённых копий: {n_damaged} (5 seed x 100, по 20 на тип)")
    lines.append(f"корректных контролей: {n_control}")
    lines.append("доля обнаружения по seed (полная / простая):")
    for s in SEEDS:
        lines.append(f"  seed {s}: полная={per_seed_full[s]:.4f}, простая={per_seed_simple[s]:.4f}")
    lines.append(f"разброс по seed: полная={spread_full:.4f}, простая={spread_simple:.4f}")
    lines.append(f"доля обнаружения полной проверкой (всего): {full_det_rate:.4f}")
    lines.append(f"доля обнаружения простой проверкой (всего): {simple_det_rate:.4f}")
    lines.append(f"ложные срабатывания полной: {full_fp_rate:.4f}, простой: {simple_fp_rate:.4f}")
    lines.append(f"парная разность (полная-простая): среднее={mean_diff:.4f}, "
                 f"95% bootstrap-интервал=[{lo:.4f}, {hi:.4f}] "
                 f"(bootstrap: {BOOTSTRAP_N} повторов, seed {BOOTSTRAP_SEED})")
    lines.append(f"статистическое преимущество (нижняя граница > 0): {stat_adv}")
    lines.append(f"практическое преимущество (>= {PRACTICAL_THRESHOLD * 100:.0f} п.п.): {pract_adv}")
    lines.append(f"все предусмотренные повреждения отклонены полной проверкой: {full_all_detected}")
    lines.append(f"ложных срабатываний нет: {no_fp}")
    lines.append("примечание: корректные контроли — повторения одной исходной таблицы; "
                 "500 повреждений могут содержать одинаковые случаи; это не 500 независимых "
                 "биологических образцов.")
    all_ok = (full_all_detected and no_fp and stat_adv and pract_adv)
    lines.append(f"ИТОГ: {'ПРОЙДЕН' if all_ok else 'НЕ ПРОЙДЕН'}")
    return rows_out, lines, all_ok


def main():
    results_dir = "results/hw2"
    os.makedirs(results_dir, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="hw2_")
    try:
        # Синтетические примеры.
        syn_lines, syn_ok = synthetic_examples(tmpdir)
        with open(os.path.join(results_dir, "synthetic_examples.txt"), "w") as f:
            f.write("Синтетические примеры (ожидаемый код и свойство)\n")
            f.write("\n".join(syn_lines) + "\n")
            f.write(f"ИТОГ: {'ПРОЙДЕН' if syn_ok else 'НЕ ПРОЙДЕН'}\n")

        # Эксперимент К4.
        rows_out, k4_lines, k4_ok = run_k4(tmpdir)
        with open(os.path.join(results_dir, "k4_experiment.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seed", "copy", "type", "full_detected", "simple_detected", "is_control"])
            w.writerows(rows_out)
        with open(os.path.join(results_dir, "k4_summary.txt"), "w") as f:
            f.write("\n".join(k4_lines) + "\n")

        print("Синтетические примеры:")
        for l in syn_lines:
            print("  " + l)
        print()
        print("Эксперимент К4:")
        for l in k4_lines:
            print("  " + l)
        return 0 if (syn_ok and k4_ok) else 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())