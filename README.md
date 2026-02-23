# Organizational Structure API

## Конфигурация

Для конфигурации приложения используется файл `.env`, скопируйте файл [`.env.example`](.env.example) и переименуете его в `.env`.

## Запуск с помощью *Docker*

> [!WARNING]
> *Docker* должен быть установлен на вашем устройстве!

Для запуска приложения с помощью *Docker* введите следующую команду:
```sh
docker compose up -d
```

Приложение будет доступно по адресу `http://localhost:8000`, или на порте, указанном в переменной `APP_PORT` в файле `.env`.

## Архитекртура

В основе архитектуры приложения стоят паттерны Dependency Injection, Unit Of Work и Repository. Вся работа с базой данных изолирована в репозиториях ([`DepartmentRepository`](src/department/repository.py) и [`EmployeeRepository`](src/employee/repository.py)). За работу с сессией отвечает [`UnitOfWork`](src/unit_of_work.py). Бизнес-логика изолирована в [`сервисе`](src/department/service.py), за передачу экземпляра `UnitOfWork` в сервис отвечает внедрение зависимостей, раелизованое *FastAPI*.
