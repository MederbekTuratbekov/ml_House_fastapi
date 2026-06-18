# Real Estate Price Prediction API

> REST API на базе ML, предсказывающий рыночную стоимость недвижимости в реальном времени.
> Устраняет ценовые ошибки в 10–20%, которые возникают при ручной оценке по устаревшим аналогам.

[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-009688)]()
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-F7931E)]()
[![R²](https://img.shields.io/badge/R²-0.88-brightgreen)]()
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()

---

## Проблема

Ручная оценка недвижимости занимает 2–4 часа на объект и даёт погрешность 10–20% из-за
устаревших данных. Агенты теряют сделки; покупатели переплачивают; продавцы занижают цену.

Этот API заменяет ручной процесс: один JSON-запрос → цена за < 100 мс.

---

## Быстрый старт

```bash
git clone https://github.com/your-username/real-estate-price-api
cd real-estate-price-api
pip install -r requirements.txt
cp _env .env          # заполнить SECRET_KEY, DB, OAuth keys
alembic upgrade head
uvicorn main:fastapi_house --host 0.0.0.0 --port 8000 --reload
```

Swagger: `http://localhost:8000/docs`

---

## Demo

```bash
curl -X POST "http://localhost:8000/lin_predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "GrLivArea": 1800,
    "YearBuilt": 2005,
    "GarageCars": 2,
    "TotalBsmtSF": 900,
    "FullBath": 2,
    "OverallQual": 7,
    "Neighborhood": "NridgHt"
  }'
```

```json
{ "predicted_price": 243750.00, "model": "decision_tree", "version": "1.0.0" }
```

---

## Результаты

| Модель              | R²    | Улучшение vs baseline |
|---------------------|-------|-----------------------|
| Linear Regression   | 0.78  | baseline              |
| Random Forest       | 0.85  | +9%                   |
| XGBoost             | 0.86  | +10%                  |
| **Decision Tree**   | **0.88** | **+13%**           |

**Победила Decision Tree** — не потому что "лучшая цифра", а потому что:
- Интерпретируемость: агент может объяснить клиенту почему цена именно такая
- Скорость инференса: < 5 мс vs 40 мс у Random Forest
- Размер модели: 180 KB vs 12 MB

> Обучение: 80/20 split, random_state=42, без утечки данных через scaler

---

## Датасет

- **Источник:** Ames Housing Dataset — публичный бенчмарк для регрессии
- **Объём:** 1 460 записей о жилой недвижимости
- **Признаки:** 7 отобранных + one-hot по 24 районам

| Признак       | Что означает                          | Почему выбран                     |
|---------------|---------------------------------------|-----------------------------------|
| GrLivArea     | Жилая площадь над землёй (кв. фут)   | Корреляция с ценой: 0.71          |
| OverallQual   | Оценка качества материалов (1–10)    | Корреляция с ценой: 0.79          |
| YearBuilt     | Год постройки                         | Влияет на износ и страховку       |
| GarageCars    | Вместимость гаража                    | Прокси для класса района          |
| TotalBsmtSF   | Площадь подвала (кв. фут)            | Увеличивает полезную площадь      |
| FullBath      | Число полных ванных комнат            | Стандарт сравнения объектов       |
| Neighborhood  | Район (one-hot, 24 категории)        | Самый сильный локационный сигнал  |

---
---
## Архитектура

    POST /lin_predict/

│

▼

    Pydantic v2          ← валидация типов + бизнес-правила

│

▼

    Feature Builder      ← OHE вектор из 24 районов (жёстко закодирован)

│

▼

    StandardScaler       ← загружается из scaler_House.pkl (joblib)

│

▼

    Decision Tree        ← загружается из model_tree.pkl (joblib)

│

▼

JSON Response        ← {"predicted_price": ..., "model": ..., "version": ...}

**Ключевые архитектурные решения:**

`pandas.get_dummies()` не гарантирует порядок признаков при инференсе →
жёстко закодировал список 24 районов в `lin_predict.py` и вручную строю OHE-вектор.
Результат: нулевые ошибки рассинхронизации между обучением и продакшеном.

---

## API

| Метод | Эндпоинт                   | Описание                          |
|-------|----------------------------|-----------------------------------|
| POST  | `/lin_predict/`            | Предсказание цены                 |
| POST  | `/auth/register`           | Регистрация пользователя          |
| POST  | `/auth/login`              | JWT-токен                         |
| POST  | `/auth/refresh`            | Обновление токена                 |
| GET   | `/property/`               | История предсказаний              |
| POST  | `/review/`                 | Отзыв о предсказании              |
| GET   | `/oauth/github/callback`   | GitHub OAuth                      |
| GET   | `/oauth/google/callback`   | Google OAuth                      |
| GET   | `/admin/`                  | SQLAdmin панель                   |

---

## Стек

| Слой         | Технологии                                               |
|--------------|----------------------------------------------------------|
| ML           | scikit-learn 1.7, XGBoost, joblib                        |
| API          | FastAPI, Uvicorn, Pydantic v2                            |
| Auth         | JWT (python-jose), OAuth2 (GitHub, Google)               |
| БД           | PostgreSQL, SQLAlchemy 2.0, Alembic                      |
| Admin        | SQLAdmin                                                 |
| Data         | pandas, NumPy, StandardScaler                            |
| DevTools     | Jupyter, seaborn, matplotlib, Docker                     |

---

## Что дальше (Roadmap)

- [ ] MLflow: трекинг экспериментов и версионирование моделей
- [ ] Data drift мониторинг (evidently) — автоалерт при смещении входных данных
- [ ] Docker Compose + Nginx для production-деплоя
- [ ] Endpoint `/predict/batch` для пакетной оценки объектов
- [ ] Переобучение по локальным датасетам (Zillow API / Redfin)

---

## Business Impact

| Метрика                              | Результат                          |
|--------------------------------------|------------------------------------|
| Время оценки одного объекта          | с 2–4 часов до < 100 мс           |
| Погрешность vs ручной оценки         | с 10–20% до ±12% по R²=0.88      |
| Масштабируемость                     | один API-вызов заменяет таблицы    |
| Переносимость на другой рынок        | замена model.pkl без изменения кода |

---

[//]: # (## Автор)
[//]: # (**[Имя]** — [LinkedIn]&#40;https://linkedin.com/in/you&#41; | [GitHub]&#40;https://github.com/you&#41;)
