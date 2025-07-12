# Python Advanced Final Project

Асинхронный REST API сервис на **FastAPI**, с хранилищем в **PostgreSQL**, развёртывается через **Docker Compose** и проксируется через **Nginx**.

---

## 🔧 Содержание

- [Функциональность](#functional)
- [Технологии](#technologies)
- [Установка](#installation)
- [Запуск](#run)

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
- (В перспективе: **Alembic, JWT, pytest**)

  [//]: # (- **pytest** + **pytest-asyncio** — тестирование)

---

## 🚀 Установка <a id="installation"></a>

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

## 🏗️ Запуск <a id="run"></a>

Собрать и запустить весь стек через Docker Compose:
```bash
docker-compose up --build
```

---

## 🗂️ Структура проекта <a id="structure"></a>

```
├── app/                # Основной код приложения
│ ├── main.py           # Точка входа в приложение
│ ├── models.py         # SQLAlchemy модели
│ ├── crud.py           # CRUD-операции
│ ├── schemas.py        # Pydantic-схемы
│ ├── database.py       # Подключение к БД
│ └── init.py
├── Dockerfile          # Сборка FastAPI-приложения
├── docker-compose.yml  # Контейнеры: app, db, nginx
├── nginx/
│ └── default.conf      # Конфигурация обратного прокси
├── static/             # Папка для статики
├── .env                # Переменные окружения
├── .env.example        # Пример env-файла
├── requirements.txt    # Зависимости
└── README.md
```