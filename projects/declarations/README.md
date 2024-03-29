# Гендерное неравенство на российской госслужбе: оценка на данных из антикоррупционных деклараций  

В этом разделе представлен код и дополнительные данные для воспроизводства расчётов, приведённых 
в [аналитической записке](https://cpur.ru/new-research/gendernoe-neravenstvo-na-rossijskoj-gossluzhbe/) ЦПУР «Гендерное неравенство на российской госслужбе: оценка на данных из антикоррупционных деклараций».

Мы разместили его в открытом доступе для того, чтобы наши результаты можно было воспроизвести и проверить, а также использовать какие-то части кода для других исследований.

## Структура раздела

1. **Data_generation** содержит ноутбук с кодом предобработки датасета "Доходы и имущество госслужащих: объединенные сведения из антикоррупционных деклараций сотрудников российских министерств", опубликованного в [каталоге ИНИД](https://data-in.ru/data-catalog/datasets/150/)  анализа гендерного баланса в различных разрезах.
2. **Analysis** содержит: 1) ноутбук с кодом, с помощью которого можно воспроизвести  регрессионный анализ; 2) файл с кодом проведения декомпозиции Оаксаки-Блайндера.
3. **Data** содержит дополнительные данные, которые потребуются для запуска ноутбука с регрессионным анализом.

## Как запускать

Чтобы воспроизвести вычисления, сделанные в аналитической записке, на датасете, опубликованном в [каталоге ИНИД](https://data-in.ru/), нужно:
1. Зайти в папку `data_generation` и запустить блокнот `data_generation.ipynb`. Выполнить часть с инициализацией и загрузкой исходного датасета, воспроизвести части с предобработкой датасета и анализом гендерного баланса. В результате одного из шагов предобработки быдет получен очищенный датасет, пригодный для проведения регрессионного анализа и декомпозиции Оаксаки-Блайндера - `df_declarations_for_regress.xlsx`.
2. Зайти в папку `analysis` и запустить блокнот `Declarations_anasysis.ipynb`. В качестве исходных данных загрузить в него полученный на предыдущем этапе `df_declarations_for_regress.xlsx`. Воспроизвести код регрессионного анализа.
3. В той же папке `analysis` представлен код на `R`, проводящий декомпозицию Оаксаки-Блайндера на данных `df_declarations_for_regress.xlsx`.

### Для обратной связи:

Эльвира Гизатуллина, e.gizatullina@data-in.ru

Ксения Зиндер, k.zinder@data-in.ru
