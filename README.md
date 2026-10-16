# ДЗ 1 «Среда и контекст»

Учебная работа курса «ИИ-ассистенты для исследователя. AI4Science» на
материале проекта Taraxacum (филогения по пластомам и ITS). В комплекте
ДЗ 1 — среда и цикл с точкой проверки, контекст агента, сжатие статьи,
онтология и мини-граф, поиск по библиотеке и внешний граф.

## Что в комплекте

- `AGENTS.md` — полный контекст проекта с учебным протоколом.
- `reports/HW1_REPORT.md` — итоговый отчёт (что сделано, кто что делал,
  как проверено, что не получилось, журналы).
- `reports/HW1_CONTEXT_EXAMPLES.md` — примеры запросов к локальному
  контексту.
- `scripts/hw1_fasta_stats.py` — расчёт статистики трёх FASTA;
  `results/hw1/fasta_stats.csv` — результат.
- `checks/check_hw1_fasta.py` — независимая проверка.
- `paper/angiosperm_2026/`, `memory/L1.md`, `memory/L2.md`, `memory/L3.md`
  — статья APG V и каскадное сжатие.
- `ontology.yaml`, `ontology/`, `notes/`, `tasks/`, `graph_view.md` —
  онтология и мини-граф.
- `reports/my_search_report.md`, `notes/` — поиск по библиотеке и внешний
  граф (OpenAlex, Wikidata).
- `reports/agent_runs/` — журналы прогонов ai4science.

## Как запустить проверку

```bash
python3 checks/check_hw1_fasta.py
```

Ожидаемый результат — код 0 и строка «OK: все проверки пройдены». Проверка
сверяет SHA-256 оригиналов `tarax/fasta_tarax/genomes/` из
`homework/inputs.tsv`, сама разбирает каждый FASTA и сверяет с
`results/hw1/fasta_stats.csv`.

## Где отчёт

- `reports/HW1_REPORT.md` — итоговый отчёт.
- `reports/HW1_CONTEXT_EXAMPLES.md` — примеры запросов к контексту.
- `INDEX.md` — полная навигация по комплекту.