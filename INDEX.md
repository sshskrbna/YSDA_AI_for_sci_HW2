# INDEX — ДЗ 1 «Среда и контекст»

Карта комплекта по фактическим файлам. Каждый путь в `…` существует.

## Что читать первым

- `README.md` — что за проект, что в комплекте, как запустить проверку.
- `reports/HW1_REPORT.md` — итоговый отчёт: что сделано, кто что делал,
  как проверено, что не получилось, журналы.
- `AGENTS.md` — полный контекст проекта с учебным протоколом (разделы 0–9).
- `STATUS.md`, `diary.md` — состояние и история учебной работы.

## Среда и цикл с точкой проверки

- `homework/inputs.tsv` — три входа и контрольные суммы (SHA-256).
- `homework/data/` — учебные FASTA (KU361241.1, KU736960.1, NC_032056.1);
  `tarax/fasta_tarax/genomes/` — три соответствующих исходных файла.
- `scripts/hw1_fasta_stats.py` — расчёт статистики FASTA (функция
  `sequence_stats()`).
- `checks/check_hw1_fasta.py` — независимая проверка (функция `verify()`).
- `results/hw1/fasta_stats.csv` — результат (три строки, gc_percent с 8
  знаками).
- `cascade.sh` — каскадное сжатие статьи L1–L3.

## Статья и контекст

- `paper/angiosperm_2026/source.pdf` — оригинал APG V;
  `paper/angiosperm_2026/source.txt` — текст по страницам;
  `paper/angiosperm_2026/source.json` — происхождение;
  `paper/angiosperm_2026/reference.bib` — библиография;
  `paper/angiosperm_2026/LICENSE_SOURCE.md` — лицензия.
- `paper/parts/part_01.md` … `paper/parts/part_12.md` — части статьи.
- `memory/L1/part_01.md` … `memory/L1/part_12.md` — сжатие каждой части.
- `memory/L1.md` — реферат по частям (строка «Статья:» заполнена);
  `memory/L2.md` — тезисы и таблица сверки с оригиналом; `memory/L3.md` —
  одна строка.
- `reports/HW1_CONTEXT_EXAMPLES.md` — примеры запросов к локальному
  контексту.

## Онтология и мини-граф

- `ontology.yaml` — онтология строения пластома Taraxacum (9 классов,
  7 отношений, 7 правил П1–П7, 2 правила Л1–Л2, 5 вопросов).
- `ontology/` — заметки классов (Образец, Пластом, ОбластьПластома,
  Граница, Задача, Файл, Результат, Проверка, Источник, Автор,
  ЗапросКГрафу).
- `notes/` — заметки объектов: 3 Образца, 3 Пластома, 4 ОбластиПластома и
  4 Границы для NC_032056.1, Результат, Проверка, 5 Источников, 5 Авторов,
  2 ЗапросаКГрафу.
- `tasks/` — задачи (Посчитать статистику FASTA — принята; Описать строение
  пластомов в графе — принята; Собрать литературу к проекту — выполнена).
- `graph_view.md` — Mermaid-схема графа; `.obsidian/` — настройки Obsidian.

## Структура пластома

- `homework/structure/ir_boundaries.csv` — границы LSC/SSC/IR трёх образцов
  (скопирован из полного проекта, см. `homework/structure/README.md`).

## Поиск по библиотеке и внешний граф

- `reports/my_search_report.md` — пять поисковых запросов и авторские
  наблюдения `[написано]`.
- `notes/Запрос 2026-10-17 OpenAlex Taraxacum chloroplast.md`,
  `notes/Запрос 2026-10-17 Wikidata Taraxacum.md` — запросы к внешним
  графам (type: ЗапросКГрафу).
- Заметки источников: `notes/Kim 2016.md`, `notes/Salih 2017.md`,
  `notes/Mouri 2024.md`, `notes/Yang 2024.md`, `notes/Salih 2017 б.md`.

## Журналы и отчёты

- `reports/agent_runs/` — журналы прогонов ai4science (cascade, fasta,
  ontology, graph, literature, report и др.).
- `reports/agent_doctor.json` — диагностика окружения.
- `reports/HW1_REPORT.md`, `reports/HW1_CONTEXT_EXAMPLES.md` — отчёт и
  примеры запросов.