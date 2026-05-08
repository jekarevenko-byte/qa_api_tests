# Автотесты API — проект контроля качества

Автоматизированный набор тестов API, созданный на основе **pytest** +**queries**, ориентированный на [JSONPlaceholder](https://jsonplaceholder.typicode.com) в качестве демонстрационного REST API. Проект разработан как реальный шаблон: чистая структура, типизированные модели, пользовательские утверждения и конвейер CI, готовый к внедрению в любой проект.


# Структура проекта

qa_api_tests/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions CI
│
├── configs/
│   └── config.py              # Env-based configuration (BASE_URL, timeout, etc.)
│
├── src/
│   ├── clients/
│   │   ├── base_client.py     # requests.Session wrapper with logging
│   │   ├── users_client.py    # /users endpoint methods
│   │   └── posts_client.py    # /posts endpoint methods
│   ├── models/
│   │   └── schemas.py         # Pydantic response models (UserModel, PostModel, …)
│   └── utils/
│       ├── assertions.py      # Custom assertion helpers
│       └── factories.py       # Faker-based test data factories
│
├── tests/
│   ├── api/
│   │   ├── test_users.py      # CRUD + negative tests for /users
│   │   └── test_posts.py      # CRUD + negative + parametrised tests for /posts
│   └── integration/
│       └── test_user_posts_flow.py  # Cross-resource consistency tests
│
├── reports/                   # Auto-generated HTML reports (gitignored)
├── .env.example               # Environment variable template
├── conftest.py                # Shared fixtures (clients, seed IDs)
├── pytest.ini                 # pytest configuration & markers
└── requirements.txt           # Python dependencies


# Quick Start

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

---

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

## Пользовательские утверждения

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

---

## Маркеры

| Marker | Description |
|---|---|
| `smoke` | Fast, critical path tests |
| `regression` | Full regression suite |
| `users` | /users endpoint tests |
| `posts` | /posts endpoint tests |
| `negative` | Error / 4xx path tests |

---

## Действия CI / GitHub

The pipeline in `.github/workflows/tests.yml` runs on every push and PR:

1. Installs dependencies
2. Runs **smoke** tests first (fast gate)
3. Runs the **full suite**
4. Uploads the **HTML report** as an artifact

Matrix: Python 3.11 and 3.12.

---

## Зависимости

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `requests` | HTTP client |
| `pydantic` | Response schema validation |
| `faker` | Test data generation |
| `pytest-html` | HTML test reports |
| `pytest-xdist` | Parallel test execution |
| `python-dotenv` | Environment variable loading |

---

