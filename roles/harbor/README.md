# harbor role

Ansible-роль для автоматической установки и настройки приватного Docker Registry на базе **Harbor**.

Роль устанавливает Harbor, настраивает Docker для работы с локальным registry, запускает сервисы Harbor и выполняет публикацию Docker-образов с автоматическим формированием тега на основе digest образа.

Основная идея роли — получать неизменяемый тег образа вместо использования только `latest`.

Пример результата:

```
nginx:latest
        |
        v
192.168.0.102:8081/library/nginx:5a88c9c4
```

Где `5a88c9c4` — часть SHA digest исходного образа.

---

## Возможности

Роль выполняет следующие задачи:

- установка Harbor из offline installer;
- генерация конфигурации Harbor;
- настройка HTTP registry без HTTPS (для лабораторных окружений);
- настройка Docker `insecure-registries`;
- запуск Harbor через Docker Compose;
- ожидание готовности Harbor API;
- авторизация в Harbor registry;
- загрузка исходного Docker-образа;
- получение digest образа;
- создание нового тега на основе SHA;
- push образа в Harbor;
- проверка опубликованных артефактов через Harbor API.

---

## Структура роли

```
roles/harbor/
├── defaults/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── install.yml
│   ├── docker.yml
│   ├── deploy.yml
│   └── image.yml
└── README.md
```

---

## Основные переменные

Основные настройки находятся в:

```
roles/harbor/defaults/main.yml
```

Пример:

```yaml
harbor_version: "2.14.0"

harbor_dir: /opt/harbor

harbor_hostname: "192.168.0.102"
harbor_port: 8081

harbor_username: admin
harbor_admin_password: "Harbor12345"

source_image: nginx:latest

harbor_project: library
harbor_image_name: nginx

digest_length: 8
```

### Описание переменных

| Переменная | Назначение |
|---|---|
| `harbor_version` | Версия Harbor |
| `harbor_dir` | Каталог установки Harbor |
| `harbor_hostname` | Адрес Harbor registry |
| `harbor_port` | Порт Harbor |
| `source_image` | Исходный Docker image |
| `harbor_project` | Проект в Harbor |
| `harbor_image_name` | Имя образа в Harbor |
| `digest_length` | Количество символов SHA, используемых в теге |

---

## Публикация образов

После получения digest образ получает новый тег:

```
source image:

nginx:latest


Harbor image:

192.168.0.102:8081/library/nginx:5a88c9c4
```

В Harbor могут существовать оба тега:

```
library/nginx

├── latest
└── 5a88c9c4
```

`latest` удобен для разработки, а SHA-тег позволяет точно определить версию образа и использовать его для rollback или Kubernetes deployment.

---

## Использование

Пример playbook:

```yaml
---
- hosts: docker
  become: true

  roles:
    - harbor
```

Запуск:

```bash
ansible-playbook -i inventory site.yml
```

---

## Требования

- Ansible 2.12+
- Docker Engine
- Docker Compose plugin
- Linux host
- доступ к загрузке Harbor installer

---

## Ограничения

Текущая конфигурация рассчитана на лабораторное окружение:

- Harbor работает по HTTP;
- используется `insecure-registries`;
- HTTPS и сертификаты не настроены;
- используется административная учетная запись Harbor.

Для production рекомендуется:

- включить HTTPS;
- использовать Harbor robot accounts;
- настроить Kubernetes `imagePullSecrets`;
- хранить учетные данные через Ansible Vault.

---

## Назначение

Роль предназначена для учебных стендов, домашних лабораторий и демонстрации процесса:

```
Docker image
      |
      v
Ansible automation
      |
      v
Harbor Registry
      |
      v
Docker / Kubernetes clients
```

