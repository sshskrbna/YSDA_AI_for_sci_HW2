---
type: ЗапросКГрафу
source: Wikidata
retrieved: 2026-10-17
---
# Запрос 2026-10-17 Wikidata Taraxacum

Инструмент и аргументы: wikidata_search, text="Taraxacum" (language=ru, limit=5); wikidata_sparql, SELECT родительского таксона (P171) для wd:Q30024
Найдено: wikidata_search — 5 сущностей, выбрана Q30024 (одуванчик, род); wikidata_sparql — 1 строка; отобрано в проект: 1 — родительский таксон Q134662 (Cichorieae)

```sparql
SELECT ?parent ?parentLabel WHERE {
  wd:Q30024 wdt:P171 ?parent .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
```

Ответ: Q30024 (Taraxacum, одуванчик) → P171 → Q134662 (Cichorieae).

Сведения внесены в заметки: [[Образец NC_032056.1]], [[Образец KU361241.1]], [[Образец KU736960.1]].

## Связи
- тип: [[ЗапросКГрафу]]