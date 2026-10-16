# Границы областей пластома — три учебных образца

`ir_boundaries.csv` — строки KU361241, KU736960, NC_032056 из
`AI_tarax/results/plastome_20261015/ir_boundaries.csv` (полный проект), без изменений.

- Координаты 1-based, включительно; `ir1` и `ir2` — две копии IR, между ними SSC,
  до `ir1_start` — LSC.
- `sample_id` без версии: KU361241 = KU361241.1 и т. д. Соответствие подтверждается
  длиной: `ir2_end` равен `length_bp` в `results/hw1/fasta_stats.csv`.
