# Python Advanced Final Project

Асинхронный REST API сервис на **FastAPI**, с хранилищем в **PostgreSQL**, развёртывается через **Docker Compose** и проксируется через **Nginx**.

---

## 🔧 Содержание

- [Функциональность](#functional)
- [Технологии](#technologies)
- [Установка](#installation)
- [Запуск](#run)
- [Структура проекта](#structure)
- [Тестирование](#testing)

---

## 🌐 Функциональность<a id="functional"></a>

- Асинхронный REST API на FastAPI
- Подключение к PostgreSQL через SQLAlchemy + asyncpg
- CRUD-операции для сущностей (пользователи, задачи)
- Работа с токенами авторизации
- Документация API через Swagger
- Docker + docker-compose
- Обратный прокси Nginx

---

## 🛠️ Технологии <a id="technologies"></a>

- **FastAPI** — асинхронный web framework на Python
- **SQLAlchemy** + **asyncpg** — async-подключение к PostgreSQL
- **PostgreSQL** — реляционная БД
- **Uvicorn** — ASGI-сервер
- **Docker & Docker Compose** — контейнеризация
- **Nginx** — обратный прокси
- **Pydantic** — валидация данных
- **Pytest** — тестирование

  [//]: # (- **pytest** + **pytest-asyncio** — тестирование)

---

## 🏗️ Установка <a id="installation"></a>

1. Клонировать репозиторий:
    ```bash
    git clone https://github.com/BarIlya77/Python_advanced_final.git
    cd Python_advanced_final
    ```
2. Создать `.env`-файл (см. [пример `.env.example`](./.env.example)), указав:
    - `POSTGRES_USER`
    - `POSTGRES_PASSWORD`
    - `POSTGRES_DB`
    - `DB_HOST`
    - `DB_PORT`

---

## 🚀 Запуск <a id="run"></a>

Собрать и запустить весь стек через Docker Compose:
```bash
docker-compose up --build
```

---

## 🗂️ Структура проекта <a id="structure"></a>

```
├── app/                     # Основной код приложения
│ ├── main.py                # Точка входа в приложение
│ ├── models.py              # SQLAlchemy модели
│ ├── crud.py                # CRUD-операции
│ ├── schemas.py             # Pydantic-схемы
│ ├── database.py            # Подключение к БД
│ └── init.py
├── Dockerfile               # Сборка FastAPI-приложения
├── docker-compose.yml       # Контейнеры: app, db, nginx
├── docker-compose.test.yml  # Контейнер для запуска тестов
├── nginx/
│ └── default.conf           # Конфигурация обратного прокси
├── tests/                   # Тесты
│ ├── conftest.py            # Конфигурация и фикстуры
│ ├── test_healthcheck.py    # Тест запуска приложения
│ ├── test_main.py           # Unit-тесты
│ └── init.py
├── static/                  # Папка для статики
├── .env                     # Переменные окружения
├── .env.example             # Пример env-файла
├── requirements.txt         # Зависимости
└── README.md
```

## 🗂️ Тестирование <a id="testing"></a>

Запуск тестов через Docker Compose:
```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```
