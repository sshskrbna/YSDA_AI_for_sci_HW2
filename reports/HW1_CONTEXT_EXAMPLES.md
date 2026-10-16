# Примеры запросов к локальному контексту

Четыре примера запросов к локальному контексту проекта: вопрос, какие файлы
нужно открыть, ответ с путями и числами из файлов. Все пути и числа взяты из
фактических файлов комплекта.

## 1. Где считается GC и чем проверено

**Вопрос.** В каком файле и какой функцией вычисляется доля GC? Где
независимая проверка? Какие файлы содержат краткий контекст статьи APG V?

**Какие файлы открыть.** `scripts/hw1_fasta_stats.py`, `checks/check_hw1_fasta.py`,
`memory/L1.md`, `memory/L2.md`, `memory/L3.md`.

**Ответ.** Доля GC вычисляется в `scripts/hw1_fasta_stats.py` функцией
`sequence_stats()`: `gc_percent = (g+c)/(a+c+g+t)*100` с 8 знаками после
запятой (знаменатель — A+C+G+T, неоднозначные основания в длину входят, но
не в знаменатель). Независимая проверка — `checks/check_hw1_fasta.py`
функцией `verify()`: сама разбирает каждый FASTA и сверяет с
`results/hw1/fasta_stats.csv` (целые точно, gc_percent с допуском 1e-6).
Краткий контекст статьи APG V — `memory/L1.md` (реферат по частям),
`memory/L2.md` (тезисы и таблица сверки), `memory/L3.md` (одна строка).

## 2. Координаты областей пластома NC_032056.1

**Вопрос.** Какие координаты и длины имеют LSC, SSC и две копии IR у
пластома NC_032056.1?

**Какие файлы открыть.** `homework/structure/ir_boundaries.csv`,
`notes/Пластом NC_032056.1.md`, заметки `notes/Область *.md`.

**Ответ.** Из `homework/structure/ir_boundaries.csv` (координаты 1-based,
включительно): LSC 1..83862 (длина 83862 bp), IR1 83863..108283
(24421 bp), SSC 108284..126861 (18578 bp), IR2 126862..151282 (24421 bp).
`ir2_end` = 151282 совпадает с `length_bp` в `results/hw1/fasta_stats.csv`.
Пластом кольцевой, IR2 граничит с LSC. Области и границы построены только
для NC_032056.1; у KU361241.1 и KU736960.1 их нет.

## 3. Какие тезисы L2 сверены с PDF

**Вопрос.** Какие тезисы в `memory/L2.md` сверены с оригиналом PDF и каков
итог сверки?

**Какие файлы открыть.** `memory/L2.md`, `paper/angiosperm_2026/source.pdf`,
`paper/angiosperm_2026/source.txt`.

**Ответ.** В таблице «Сверка с оригиналом» сверены тезисы 2, 3 и 4.
Тезис 2 — «APG V accepts 407 families.» (с. 5) — подтверждено. Тезис 3 —
«Gotty & Pillon (2025) found that since 2012 (when the APG III, 2009,
classification was implemented), family-level changes have been reduced to
zero.» (с. 5) — расходится: в оригинале снижение до нуля с момента
внедрения APG III (2009), а не «между APG IV и APG V»; тезис исправлен.
Тезис 4 — «fabids should be limited just to the nitrogen-fixing members,
Cucurbitales, Rosales, Fagales, and Fabales.» (с. 11) — подтверждено.
Сверка цитат по PDF выполнена вручную (2026-10-14).

## 4. Какие источники найдены каким запросом

**Вопрос.** Какие опубликованные работы о пластомах Taraxacum найдены и
каким запросом к внешнему графу?

**Какие файлы открыть.** `notes/Запрос 2026-10-17 OpenAlex Taraxacum chloroplast.md`,
`notes/Запрос 2026-10-17 Wikidata Taraxacum.md`, заметки `notes/Kim 2016.md`,
`notes/Salih 2017.md`, `notes/Mouri 2024.md`, `notes/Yang 2024.md`,
`notes/Salih 2017 б.md`.

**Ответ.** OpenAlex: `openalex_search` query="Taraxacum chloroplast genome",
sort=relevance, limit=15 — найдено 1019, отобрано 5 работ, в названии
которых есть Taraxacum или dandelion и одно из слов chloroplast, plastome,
plastid: Kim 2016 (W2518726131), Salih 2017 (W2587673157), Mouri 2024
(W4401400231), Yang 2024 (W4396801559), Salih 2017 б (W2593840457).
Wikidata: `wikidata_search` «Taraxacum» → Q30024; `wikidata_sparql` по P171
→ Q134662 (Cichorieae). Связь цитирует подтверждена только у Mouri 2024
(цитирует Salih 2017 и Kim 2016). Первый отбор по цитированиям дал работы
не по теме и был переделан.