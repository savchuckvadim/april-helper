src/
├── api/                   # Общая API логика
│   ├── clients/           # Клиенты для взаимодействия с внешними API
│   │   ├── __init__.py
│   │   ├── bx_action/     # Клиент для работы с BXAction
│   │   │   ├── __init__.py
│   │   │   ├── bx_action_api.py  # Реализация API клиента
│   │   │   └── dto.py            # Общие DTO для клиента
│   │   ├── beeline/       # Клиент для работы с Beeline
│   │   │   ├── __init__.py
│   │   │   ├── beeline_api.py    # Реализация API клиента
│   │   │   └── dto.py            # DTO для Beeline
│   │   └── other_client/  # Другие клиенты (пример)
│   │       ├── __init__.py
│   │       └── other_api.py
│   ├── endpoints/         # Общие эндпоинты
│   │   ├── __init__.py
│   │   ├── common.py             # Общие маршруты
│   │   ├── health_check.py       # Маршруты для проверки состояния
│   │   └── helpers/       # Вспомогательные маршруты
│   │       ├── __init__.py
│   │       ├── file_helpers.py   # Маршруты для работы с файлами
│   │       └── auth_helpers.py   # Маршруты для аутентификации
│   └── entities/          # Общие сущности
│       ├── __init__.py
│       ├── base_model.py         # Базовые модели
│       └── other_entities.py     # Другие общие сущности
├── core/                  # Основные настройки и конфигурации
│   ├── __init__.py
│   ├── settings/          # Конфигурационные файлы
│   │   ├── __init__.py
│   │   ├── config.py              # Основная конфигурация
│   │   └── logging_config.py      # Логирование
│   ├── db.py              # Логика подключения к базе данных
│   └── app.py             # Основное приложение FastAPI
├── modules/               # Модули приложения
│   ├── audio/             # Пример модуля (Audio)
│   │   ├── api/           # API модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_endpoints.py # Эндпоинты модуля Audio
│   │   ├── entities/      # DTO и модели модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_dto.py       # DTO для Audio
│   │   ├── model/         # Сущности модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_model.py     # Модель базы данных Audio
│   │   ├── lib/           # Вспомогательные функции и библиотеки модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_helpers.py   # Хелперы для Audio
│   │   ├── endpoints/     # Маршруты модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_routes.py    # Эндпоинты модуля Audio
│   │   ├── services/      # Логика модуля
│   │   │   ├── __init__.py
│   │   │   └── audio_service.py   # Сервисы модуля Audio
│   │   └── usecases/      # Кейсы использования
│   │       ├── __init__.py
│   │       └── process_audio.py   # Логика обработки аудио
│   ├── module2/           # Пример другого модуля
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── module2_endpoints.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   └── module2_dto.py
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── module2_model.py
│   │   ├── lib/
│   │   │   ├── __init__.py
│   │   │   └── module2_helpers.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   └── module2_routes.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── module2_service.py
│   │   └── usecases/
│   │       ├── __init__.py
│   │       └── process_module2.py
└── tests/                 # Тесты приложения
    ├── __init__.py
    ├── test_audio.py      # Тесты модуля Audio
    ├── test_endpoints.py  # Тесты общих маршрутов
    └── test_services.py   # Тесты сервисов
