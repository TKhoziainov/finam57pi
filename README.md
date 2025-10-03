# Finam x HSE Trade AI Hack - Baseline

Базовый шаблон для хакатона по созданию AI-ассистента трейдера на базе Finam TradeAPI.

## 📋 Описание

Этот проект предоставляет минимальный рабочий бейзлайн для генерации `submission.csv` - файла с предсказаниями API запросов на основе вопросов на естественном языке.

**Задача**: Преобразовать вопрос на русском языке в HTTP запрос к Finam TradeAPI
- Вход: вопрос (например, "Что по Газпрому сегодня?")
- Выход: HTTP метод (GET/POST/DELETE) + API путь (например, `/v1/instruments/GAZP@MISX/quotes/latest`)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установите Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установите зависимости проекта
poetry install
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# OpenRouter API для доступа к LLM
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini  # или другая модель
```

### 3. Генерация submission.csv

```bash
# Сгенерировать submission.csv на основе test.csv
poetry run generate-submission

# Или с кастомными параметрами
poetry run generate-submission \
    --test-file data/processed/test.csv \
    --train-file data/processed/train.csv \
    --output-file data/processed/submission.csv \
    --num-examples 15
```

### 4. Валидация результата

```bash
# Проверить корректность submission.csv
poetry run validate-submission
```

## 📁 Структура проекта

```
├── data/
│   ├── processed/
│   │   ├── train.csv          # Обучающие примеры (100 запросов)
│   │   ├── test.csv           # Тестовые вопросы (300 запросов)
│   │   ├── sample_submission.csv  # Пример submission
│   │   └── submission.csv     # Ваш сгенерированный submission
├── docs/
│   ├── task.md                # Описание задачи
│   ├── evaluation.md          # Методология оценки
│   └── data.md                # Описание данных
├── scripts/
│   ├── generate_submission.py # Генерация submission.csv
│   └── validate_submission.py # Валидация submission.csv
├── src/app/
│   ├── config.py              # Настройки (API ключи)
│   └── llm.py                 # Обертка для вызова LLM
└── tests/
    └── test_submission_validator.py
```

## 🎯 Как это работает

1. **Few-shot Learning**: Скрипт берет случайные примеры из `train.csv` и использует их как шаблоны для LLM
2. **LLM генерация**: Для каждого вопроса из `test.csv` отправляется запрос к LLM с промптом и примерами
3. **Парсинг ответа**: Ответ LLM парсится в формат `(HTTP_METHOD, API_PATH)`
4. **Сохранение**: Результаты сохраняются в `submission.csv`

## 🔧 Улучшение бейзлайна

Этот бейзлайн специально сделан простым для легкого расширения. Возможные направления:

### Для улучшения accuracy на лидерборде:
- 🧠 Улучшите промпт (добавьте больше деталей API, структурированный вывод)
- 📚 Экспериментируйте с количеством few-shot примеров
- 🎲 Используйте более умную выборку примеров (по схожести вопросов)
- 🤖 Попробуйте другие LLM модели (GPT-4, Claude и т.д.)
- 🔄 Добавьте retry логику с улучшенным промптом при неудаче
- ✅ Добавьте post-processing для исправления типичных ошибок

### Для продвинутых кейсов (30% оценки):
- 💬 Добавьте чат-интерфейс (Streamlit, Gradio, FastAPI + фронтенд)
- 📊 Реализуйте визуализацию данных (графики цен, портфель)
- 🔌 Подключите реальный Finam TradeAPI SDK
- 🤝 Добавьте multi-turn диалог с контекстом
- 🎨 Создайте красивый UI/UX

## 📊 Валидация

Перед отправкой обязательно проверьте submission:

```bash
poetry run validate-submission
```

Проверяет:
- ✅ Наличие всех uid из test.csv
- ✅ Корректность HTTP методов
- ✅ Валидность API путей
- ✅ Отсутствие пустых значений
- ✅ Уникальность uid

## 🔍 Code Quality

```bash
# Форматирование кода
poetry run ruff format .

# Проверка линтером
poetry run ruff check .

# Исправление автофиксимых проблем
poetry run ruff check --fix .
```

## 📖 Документация

- [Описание задачи](docs/task.md)
- [Методология оценки](docs/evaluation.md)
- [Описание данных](docs/data.md)

## 🤝 Для организаторов

Этот бейзлайн создан как стартовая точка для 40 команд хакатона. Он:
- ✅ Минималистичен и понятен
- ✅ Легко расширяется в разных направлениях
- ✅ Дает базовую accuracy для старта
- ✅ Содержит всю необходимую инфраструктуру (валидация, скрипты)

Команды могут развивать проект в любом направлении: улучшать промпты, добавлять UI, интегрировать с реальным API, создавать сложные визуализации и т.д.
