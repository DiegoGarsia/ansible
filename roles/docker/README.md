# docker role
## Описание

Ansible-роль предназначена для автоматической установки Docker Engine на Debian-системы, подготовки простого Python Flask-приложения, сборки Docker-образа и запуска контейнера.

Роль выполняет полный цикл развертывания:

- подготовка хоста;
- установка и настройка Docker;
- копирование файлов Flask-приложения;
- сборка Docker-образа;
- запуск и управление контейнером.

Роль разработана с учетом принципов идемпотентности: повторный запуск Ansible playbook не приводит к лишним изменениям, если система уже находится в требуемом состоянии.

---

## Требования

- Ansible версии 2.16 или выше
- Debian-based система
- Доступ с правами `sudo`
- Коллекция Ansible `community.docker`

Установка коллекции:

```
ansible-galaxy collection install community.docker
```

---

## Структура роли

```
roles/docker/

├── tasks/
│   ├── main.yml          # Основной сценарий выполнения роли
│   ├── cleanup.yml       # Подготовка хоста перед развертыванием
│   ├── install.yml       # Установка Docker Engine
│   ├── build.yml         # Подготовка приложения и сборка образа
│   └── run.yml           # Запуск Docker-контейнера
│
├── files/
│   ├── app.py            # Flask приложение
│   ├── requirements.txt  # Python зависимости
│   └── Dockerfile        # Инструкция сборки Docker-образа
│
├── defaults/
│   └── main.yml          # Переменные роли по умолчанию
│
└── meta/
    └── main.yml          # Метаданные роли
```

---

## Что выполняет роль

### Подготовка системы

Перед развертыванием роль отключает ранее запущенное Flask-приложение через systemd, чтобы освободить используемые сетевые порты.

### Установка Docker

Устанавливается Docker Engine:

```
docker_packages:
  - docker.io
```

После установки сервис Docker автоматически запускается и добавляется в автозагрузку.

### Подготовка приложения

Файлы Flask-приложения копируются на сервер:

```
/opt/flask-app
```

Используемые файлы:

```
app.py
requirements.txt
Dockerfile
```

### Сборка Docker-образа

После копирования исходных файлов создается Docker-образ:

```
flask-app
```

Сборка выполняется через Ansible-модуль:

```
community.docker.docker_image
```

---

## Запуск контейнера

Контейнер запускается через:

```
community.docker.docker_container
```

Параметры контейнера:

```
name: flask-app
port:
  - 5000:5000
restart_policy: unless-stopped
```

После запуска приложение доступно по адресу:

```
http://<server-ip>:5000
```

---

## Переменные роли

Основные переменные находятся в:

```
defaults/main.yml
```

Пример:

```
docker_app_dir: /opt/flask-app

docker_image_name: flask-app

docker_container_name: flask-app

docker_host_port: 5000

docker_container_port: 5000
```

Переменные могут быть переопределены через inventory или `group_vars`.

---

## Использование

Пример playbook:

```
---
- name: Deploy Flask application
  hosts: docker
  become: true

  roles:
    - docker
```

Запуск:

```
ansible-playbook -i inventory playbook.yml
```

---

## Проверка результата

Проверить состояние контейнера:

```
docker ps
```

Пример результата:

```
CONTAINER ID   IMAGE       PORTS
xxxx           flask-app   0.0.0.0:5000->5000/tcp
```

Проверить работу приложения:

```
curl http://localhost:5000
```

Ожидаемый ответ:

```
Hello from Flask inside Docker!
```

---

## Идемпотентность

Роль поддерживает повторный запуск без изменения уже настроенного окружения.

Первый запуск:

```
changed=...
```

Повторный запуск:

```
ok=...
changed=0
failed=0
```

Ansible самостоятельно определяет необходимость установки пакетов, пересборки образа и изменения состояния контейнера.
