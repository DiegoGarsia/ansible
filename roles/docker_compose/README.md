# docker_compose role

## Описание

Данная Ansible-роль предназначена для автоматического развертывания многоконтейнерного приложения на базе Docker Compose v2. В качестве тестового приложения используется простая связка Flask frontend + Flask backend, которая демонстрирует взаимодействие контейнеров через собственную Docker-сеть, а также использование Docker volumes для хранения данных.

Роль рассчитана на использование совместно с ранее установленной ролью `docker`, которая отвечает за установку Docker Engine. В рамках данной роли выполняется только настройка Docker Compose и развертывание приложения.

## Структура роли

```text
roles/docker_compose/
├── defaults
│   └── main.yml
├── files
│   ├── app.py
│   ├── backend.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   ├── deploy.yml
│   ├── install.yml
│   ├── main.yml
│   ├── prepare.yml
│   └── run.yml
├── templates
│   └── docker-compose.yml.j2
├── tests
│   ├── inventory
│   └── test.yml
└── vars
    └── main.yml
```

## Что выполняет роль

Роль выполняет следующие действия:

1. Устанавливает Docker Compose v2 как CLI-плагин:

```text
/usr/local/lib/docker/cli-plugins/docker-compose
```

После установки становится доступна команда:

```bash
docker compose version
```

2. Создает рабочую директорию приложения:

```text
/opt/flask-compose
```

3. Копирует необходимые файлы приложения:

- Dockerfile;
- requirements.txt;
- Flask frontend приложение;
- Flask backend приложение;
- docker-compose.yml.

4. Формирует конфигурацию Docker Compose для запуска многоконтейнерного приложения.
5. Собирает Docker-образы для сервисов:

- frontend;
- backend.

6. Создает собственную Docker-сеть:

```text
flask_network
```

Контейнеры взаимодействуют между собой внутри этой сети через имена сервисов Docker Compose.

7. Запускает приложение через Docker Compose v2:

```bash
docker compose up -d --build
```

8. Настраивает использование volumes для сохранения данных контейнеров.

## Используемое приложение

В рамках роли разворачивается простое Flask-приложение из двух сервисов.

### Frontend

Frontend контейнер запускает Flask-приложение, которое обращается к backend сервису через Docker-сеть.

Пример взаимодействия:

```text
frontend → backend:5000
```

### Backend

Backend контейнер предоставляет API на Flask и отвечает на запросы от frontend.

Контейнеры не используют IP-адреса, а обращаются друг к другу через DNS Docker Compose:

```text
http://backend:5000
```

## Переменные роли

Основные переменные находятся в:

```text
vars/main.yml
```

Пример:

```yaml
docker_compose_version: v2.27.0
docker_cli_plugins_dir: /usr/local/lib/docker/cli-plugins
```

Также могут использоваться значения из:

```text
defaults/main.yml
```

## Запуск роли

Пример playbook:

```yaml
- name: Deploy Flask application
  hosts: docker
  become: true
  roles:
    - docker_compose
```

Запуск:

```bash
ansible-playbook -i inventory playbook.yml
```

## Проверка результата

Проверить запущенные контейнеры:

```bash
docker ps
```

Ожидаемый результат:

```text
flask_frontend
flask_backend
```

Проверить Docker-сеть:

```bash
docker network ls
```

Должна присутствовать:

```text
flask_network
```

Проверить работу приложения:

```bash
curl http://<docker-host>:<port>
```

## Идемпотентность

Роль является идемпотентной.

Повторный запуск:

```bash
ansible-playbook -i inventory playbook.yml
```

не приводит к повторной установке компонентов и пересозданию ресурсов без необходимости.

После первого успешного запуска повторное выполнение роли завершается без ошибок:

```text
failed=0
```

## Примечание

Роль использует Docker Compose v2, поэтому используется современная команда:

```bash
docker compose
```

а не устаревшая:

```bash
docker-compose
```

Файл `docker-compose.yml` не содержит параметр `version`, так как Docker Compose v2 считает его устаревшим.
