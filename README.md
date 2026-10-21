# Автоматическая проверка REST API

[![API Tests](https://github.com/jekarevenko-byte/qa_api_tests/actions/workflows/tests.yml/badge.svg)](https://github.com/jekarevenko-byte/qa_api_tests/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-report-8A2BE2?logo=qameta&logoColor=white)](https://jekarevenko-byte.github.io/qa_api_tests/)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![pytest](https://img.shields.io/badge/pytest-8.3-green)

**[Онлайн Allure-отчёт последнего прогона](https://jekarevenko-byte.github.io/qa_api_tests/)**

Готовое решение для автоматизированного тестирования API. В основе — популярные инструменты pytest и requests, для демонстрации возможностей взят общедоступный REST API JSONPlaceholder. Проект оформлен как универсальный шаблон: он имеет продуманную структуру, включает типизированные модели данных и пользовательские проверки, а также содержит готовый конвейер CI. Достаточно взять за основу — и можно сразу адаптировать под свой проект.

## Структура проекта

```qa_api_tests/
├── configs/config.py              ← BASE_URL, timeout из .env
├── src/
│   ├── clients/
│   │   ├── base_client.py         ← requests.Session + логирование
│   │   ├── users_client.py        ← методы /users
│   │   └── posts_client.py        ← методы /posts
│   ├── models/schemas.py          ← Pydantic-модели (UserModel, PostModel, …)
│   └── utils/
│       ├── assertions.py          ← кастомные хелперы assert_ok / assert_schema / …
│       └── factories.py           ← Faker-фабрики make_user() / make_post()
├── tests/
│   ├── api/test_users.py          ← 15 тестов: CRUD + negative
│   ├── api/test_posts.py          ← 16 тестов: CRUD + parametrize + filter
│   └── integration/test_user_posts_flow.py  ← cross-resource consistency
├── conftest.py                    ← session-scope фикстуры
├── pytest.ini                     ← markers, HTML/Allure-отчёты, логирование
├── .github/
│   ├── workflows/tests.yml        ← GitHub Actions: тесты + Allure-отчёт на Pages
│   ├── allure/categories.json     ← категории дефектов в отчёте
│   └── dependabot.yml             ← автообновление зависимостей и actions
└── README.md
```

# Старт

### 1. Создание виртуальной среды

```bash
cd qa-api-tests
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте среду

```bash
cp .env.example .env
# При необходимости отредактируйте .env (по умолчанию jsonplaceholder.typicode.com)
```

### 4. Запуск тестов

```bash
# All tests
pytest

# Smoke tests only (fast, ~10 s)
pytest -m smoke

# Users or posts only
pytest -m users
pytest -m posts

# Negative tests
pytest -m negative

# Full regression
pytest -m regression

# Parallel execution (4 workers)
pytest -n 4

# With verbose output + HTML report
pytest -v --html=reports/report.html
```

После любого запуска результаты Allure лежат в `allure-results/` (см. раздел «Allure-отчёт»).

## Архитектура

### Многоуровненвый дизайн

```
Tests  →  Clients  →  BaseClient (requests.Session)  →  API
              ↓
          Assertions + Models
```

| Layer | Role |
|---|---|
| `BaseClient` | Single session, URL joining, logging, timeout |
| `UsersClient / PostsClient` | Domain-specific methods per endpoint |
| `schemas.py` (Pydantic) | Validate response structure & types |
| `assertions.py` | Readable, informative assertion helpers |
| `factories.py` | Generate random valid payloads with Faker |
| `conftest.py` | Session-scoped fixtures shared across all tests |

---

## Что тестируется ->

### `/users` (test_users.py)
| Test | Type |
|---|---|
| GET all users → 200 + schema | smoke / schema |
| GET single user → 200 + fields | smoke |
| GET nonexistent user → 404 | negative |
| POST create user → 201 + id assigned | smoke / create |
| PUT full update → 200 + reflected | update |
| PATCH partial update → 200 + reflected | update |
| DELETE user → 200/204 | delete |
| GET user's posts → list with correct userId | relation |

### `/posts` (test_posts.py)
| Test | Type |
|---|---|
| GET all posts → 200 + schema (100 items) | smoke / schema |
| GET single post → 200 | smoke |
| GET posts parametrised (IDs 1,5,10,50,100) | parametrised |
| GET filtered by userId | filter |
| GET nonexistent post → 404 | negative |
| POST create post → 201 + id + fields | create |
| PUT / PATCH update → 200 + reflected | update |
| DELETE post → 200/204 | delete |
| GET post comments → list with correct postId | relation |

### Integration (test_user_posts_flow.py)
- All `userId` values in posts match real users
- `/users/{id}/posts` ↔ `/posts?userId={id}` return identical IDs
- Every user has at least one post

---

## Кастомные проверки

```python
from src.utils.assertions import (
    assert_ok,           # status == 200
    assert_created,      # status == 201
    assert_not_found,    # status == 404
    assert_json,         # Content-Type is JSON, returns parsed body
    assert_schema,       # Validates against Pydantic model
    assert_field_equals, # Checks specific field value
    assert_field_present,# Checks fields exist
    assert_response_time,# Checks latency < N ms
)
```

## Маркеры

| Marker | Description |
|---|---|
| `smoke` | Fast, critical path tests |
| `regression` | Full regression suite |
| `users` | /users endpoint tests |
| `posts` | /posts endpoint tests |
| `negative` | Error / 4xx path tests |

## Allure-отчёт

Каждый HTTP-вызов в тестах — это шаг Allure с вложениями **Request** и **Response** (заголовок `Authorization` в отчёт не попадает). Каждая проверка из `assertions.py` тоже отдельный шаг. Тесты сгруппированы по `epic → feature → story`, smoke-тесты помечены severity `critical`.

Локальный просмотр (нужен [Allure CLI](https://allurereport.org/docs/install/) и Java):

```bash
pytest                      # создаёт allure-results/
allure serve allure-results # собирает отчёт и открывает в браузере
```

## CI/CD: GitHub Actions

Workflow `.github/workflows/tests.yml` запускается при push в `main`/`develop`, на каждый pull request, по будням в 06:00 UTC и вручную (кнопка *Run workflow*).

| Job | Что делает |
|---|---|
| `test` (Python 3.11 и 3.12) | устанавливает зависимости → **smoke** как быстрый гейт → **полный прогон** → сохраняет `allure-results` и pytest-html как artifacts |
| `allure-report` | скачивает результаты, подтягивает историю прошлых прогонов, генерирует Allure-отчёт, пишет сводку в *Job summary* и публикует отчёт на GitHub Pages (только для `main`) |

В отчёте на Pages есть графики трендов (history) и виджет Environment (BASE_URL, Python, коммит, ветка). В pull request отчёт доступен как artifact `allure-report`.

### Однократная настройка GitHub Pages

После первого успешного прогона на `main` в репозитории появится ветка `gh-pages`. Включите публикацию:
**Settings → Pages → Source: Deploy from a branch → Branch: `gh-pages` / `(root)` → Save.**
Отчёт откроется по адресу https://jekarevenko-byte.github.io/qa_api_tests/

## Зависимости

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `requests` | HTTP client |
| `pydantic` | Response schema validation |
| `faker` | Test data generation |
| `pytest-html` | Простой HTML-отчёт |
| `allure-pytest` | Allure-отчёты: шаги, вложения, severity |
| `pytest-xdist` | Parallel test execution |
| `python-dotenv` | Environment variable loading |
