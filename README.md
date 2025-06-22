# Python Advanced Final Project

Асинхронный REST API сервис на **FastAPI**, с хранилищем в **PostgreSQL**, развёртывается через **Docker Compose** и проксируется через **Nginx**.

---

## 🔧 Содержание

- [Функциональность](#functional)
- [Технологии](#technologies)
- [Установка](#installation)
- [Запуск](#run)
- [Структура проекта](#structure)
- [Конфигурация](#config)
- [Тестирование](#testing)
- [CI/CD](#ci-cd)
- [Поддержка и вклад](#contributing)

---

## 🌐 Функциональность <a name="functional"></a>

- Полноценный CRUD API (создание, чтение, обновление, удаление) асинхронно.
- Документация API автоматически доступна через Swagger UI.
- Логирование и обработка ошибок.
- Настраиваемые настройки через переменные окружения.

---

## 🧱 Технологии <a name="technologies"></a>

- **FastAPI** — асинхронный web framework на Python
- **SQLAlchemy** + **asyncpg** — async-подключение к PostgreSQL
- **PostgreSQL** — реляционная БД
- **Uvicorn** — ASGI-сервер
- **Docker & Docker Compose** — контейнеризация
- **Nginx** — обратный прокси
- **Pydantic** — валидация данных
- **Alembic** — миграции БД
- **pytest** + **pytest-asyncio** — тестирование

---

## 🚀 Установка <a name="installation"></a>

1. Клонировать репозиторий:
    ```bash
    git clone https://github.com/BarIlya77/Python_advanced_final.git
    cd Python_advanced_final
    ```
2. Создать `.env`-файл (см. [пример `.env.example`](./.env.example)), указав:
    - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
    - `DB_HOST`, `DB_PORT`

---

## 🏗️ Запуск <a name="run"></a>

Собрать и запустить весь стек через Docker Compose:
```bash
docker-compose up --build
