#!/usr/bin/env python3
"""
Скрипт для генерации submission.csv на основе test.csv

Использует LLM для преобразования вопросов на естественном языке
в HTTP запросы к Finam TradeAPI.

Использование:
    python scripts/generate_submission.py [OPTIONS]

Опции:
    --test-file PATH      Путь к test.csv (по умолчанию: data/processed/test.csv)
    --train-file PATH     Путь к train.csv (по умолчанию: data/processed/train.csv)
    --output-file PATH    Путь к submission.csv (по умолчанию: data/processed/submission.csv)
    --num-examples INT    Количество примеров для few-shot (по умолчанию: 10)
    --batch-size INT      Размер батча для обработки (по умолчанию: 5)
"""

import csv
import random
from pathlib import Path

import click
from tqdm import tqdm  # type: ignore[import-untyped]

from src.app.llm import call_llm


def load_train_examples(train_file: Path, num_examples: int = 10) -> list[dict[str, str]]:
    """Загрузить примеры из train.csv для few-shot learning"""
    examples = []
    with open(train_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            examples.append({"question": row["question"], "type": row["type"], "request": row["request"]})

    # Берем разнообразные примеры (GET, POST, DELETE)
    get_examples = [e for e in examples if e["type"] == "GET"]
    post_examples = [e for e in examples if e["type"] == "POST"]
    delete_examples = [e for e in examples if e["type"] == "DELETE"]

    # Формируем сбалансированный набор
    selected = []
    selected.extend(random.sample(get_examples, min(num_examples - 3, len(get_examples))))
    selected.extend(random.sample(post_examples, min(2, len(post_examples))))
    selected.extend(random.sample(delete_examples, min(1, len(delete_examples))))

    return selected[:num_examples]


def create_prompt(question: str, examples: list[dict[str, str]]) -> str:
    """Создать промпт для LLM с few-shot примерами"""
    prompt = """Ты - эксперт по Finam TradeAPI. Твоя задача - преобразовать вопрос на русском языке в HTTP запрос к API.

API Documentation:
- GET /v1/exchanges - список бирж
- GET /v1/assets - поиск инструментов
- GET /v1/assets/{symbol} - информация об инструменте
- GET /v1/assets/{symbol}/params - параметры инструмента для счета
- GET /v1/assets/{symbol}/schedule - расписание торгов
- GET /v1/assets/{symbol}/options - опционы на базовый актив
- GET /v1/instruments/{symbol}/quotes/latest - последняя котировка
- GET /v1/instruments/{symbol}/orderbook - биржевой стакан
- GET /v1/instruments/{symbol}/trades/latest - лента сделок
- GET /v1/instruments/{symbol}/bars - исторические свечи
  (параметры: timeframe, interval.start_time, interval.end_time)
- GET /v1/accounts/{account_id} - информация о счете
- GET /v1/accounts/{account_id}/orders - список ордеров
- GET /v1/accounts/{account_id}/orders/{order_id} - информация об ордере
- GET /v1/accounts/{account_id}/trades - история сделок
- GET /v1/accounts/{account_id}/transactions - транзакции по счету
- POST /v1/sessions - создание новой сессии
- POST /v1/sessions/details - детали текущей сессии
- POST /v1/accounts/{account_id}/orders - создание ордера
- DELETE /v1/accounts/{account_id}/orders/{order_id} - отмена ордера

Timeframes: TIME_FRAME_M1, TIME_FRAME_M5, TIME_FRAME_M15, TIME_FRAME_M30,
TIME_FRAME_H1, TIME_FRAME_H4, TIME_FRAME_D, TIME_FRAME_W, TIME_FRAME_MN

Примеры:

"""

    for ex in examples:
        prompt += f'Вопрос: "{ex["question"]}"\n'
        prompt += f'Ответ: {ex["type"]} {ex["request"]}\n\n'

    prompt += f'Вопрос: "{question}"\n'
    prompt += "Ответ (только HTTP метод и путь, без объяснений):"

    return prompt


def parse_llm_response(response: str) -> tuple[str, str]:
    """Парсинг ответа LLM в (type, request)"""
    response = response.strip()

    # Ищем HTTP метод в начале
    methods = ["GET", "POST", "DELETE", "PUT", "PATCH"]
    method = "GET"  # по умолчанию
    request = response

    for m in methods:
        if response.upper().startswith(m):
            method = m
            request = response[len(m) :].strip()
            break

    # Убираем лишние символы
    request = request.strip()
    if not request.startswith("/"):
        # Если LLM вернул что-то странное, пытаемся найти путь
        parts = request.split()
        for part in parts:
            if part.startswith("/"):
                request = part
                break

    # Fallback на безопасный вариант
    if not request.startswith("/"):
        request = "/v1/assets"

    return method, request


def generate_api_call(question: str, examples: list[dict[str, str]]) -> dict[str, str]:
    """Сгенерировать API запрос для вопроса"""
    prompt = create_prompt(question, examples)

    messages = [{"role": "user", "content": prompt}]

    try:
        response = call_llm(messages, temperature=0.0, max_tokens=200)
        llm_answer = response["choices"][0]["message"]["content"].strip()

        method, request = parse_llm_response(llm_answer)

        return {"type": method, "request": request}

    except Exception as e:
        click.echo(f"⚠️  Ошибка при генерации для вопроса '{question[:50]}...': {e}", err=True)
        # Возвращаем fallback
        return {"type": "GET", "request": "/v1/assets"}


@click.command()
@click.option(
    "--test-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/processed/test.csv",
    help="Путь к test.csv",
)
@click.option(
    "--train-file",
    type=click.Path(exists=True, path_type=Path),
    default="data/processed/train.csv",
    help="Путь к train.csv",
)
@click.option(
    "--output-file",
    type=click.Path(path_type=Path),
    default="data/processed/submission.csv",
    help="Путь к submission.csv",
)
@click.option("--num-examples", type=int, default=10, help="Количество примеров для few-shot")
def main(test_file: Path, train_file: Path, output_file: Path, num_examples: int) -> None:
    """Генерация submission.csv для хакатона"""
    click.echo("🚀 Генерация submission файла...")
    click.echo(f"📖 Загрузка примеров из {train_file}...")

    # Загружаем примеры для few-shot
    examples = load_train_examples(train_file, num_examples)
    click.echo(f"✅ Загружено {len(examples)} примеров для few-shot learning")

    # Читаем тестовый набор
    click.echo(f"📖 Чтение {test_file}...")
    test_questions = []
    with open(test_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            test_questions.append({"uid": row["uid"], "question": row["question"]})

    click.echo(f"✅ Найдено {len(test_questions)} вопросов для обработки")

    # Генерируем ответы
    click.echo("🤖 Генерация API запросов с помощью LLM...")
    results = []

    for item in tqdm(test_questions, desc="Обработка"):
        api_call = generate_api_call(item["question"], examples)
        results.append({"uid": item["uid"], "type": api_call["type"], "request": api_call["request"]})

    # Записываем в submission.csv
    click.echo(f"💾 Сохранение результатов в {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["uid", "type", "request"], delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    click.echo(f"✅ Готово! Создано {len(results)} записей в {output_file}")
    click.echo("\n📊 Статистика по типам запросов:")
    type_counts: dict[str, int] = {}
    for r in results:
        type_counts[r["type"]] = type_counts.get(r["type"], 0) + 1
    for method, count in sorted(type_counts.items()):
        click.echo(f"  {method}: {count}")


if __name__ == "__main__":
    main()
