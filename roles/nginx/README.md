# Nginx Reverse Proxy with Ansible

## Описание

Проект автоматизирует развёртывание **Nginx Reverse Proxy** с помощью **Ansible**.

После выполнения playbook:

- устанавливается Nginx;
- удаляется стандартный сайт (`default`);
- создаётся конфигурация Reverse Proxy;
- автоматически формируется upstream из backend-хостов, описанных в inventory;
- генерируется самоподписанный wildcard SSL-сертификат;
- Nginx начинает балансировать HTTP(S)-трафик между двумя backend-серверами.

---

## Архитектура

```
                    Client
                       │
                  https://nginx.diego.home
                       │
               ┌─────────────────┐
               │     Nginx        │
               │ 192.168.0.101    │
               └─────────────────┘
                       │
             upstream backend_servers
               ┌──────────┴──────────┐
               │                     │
       192.168.0.102           192.168.0.150
         Docker (LXC)           CentOS (KVM)
      Python HTTP Server     Python HTTP Server
```

---

## Структура проекта

```
ansible/
├── inventory.ini
├── playbook.yml
└── roles/
    └── nginx/
        ├── defaults/
        ├── handlers/
        │   └── main.yml
        ├── tasks/
        │   └── main.yml
        └── templates/
            └── reverse_proxy.conf.j2
```

---

## Inventory

Пример inventory:

```ini
[nginx_host]
nginx ansible_host=192.168.0.101

[backend]
docker ansible_host=192.168.0.102
centos ansible_host=192.168.0.150
```

Все серверы из группы `backend` автоматически добавляются в `upstream`.

---

## Возможности

Роль автоматически:

- устанавливает Nginx;
- удаляет стандартный сайт;
- генерирует конфигурацию Reverse Proxy;
- создаёт wildcard SSL-сертификат;
- включает и запускает сервис Nginx;
- проверяет корректность конфигурации перед перезапуском;
- перезапускает Nginx только при изменении конфигурации.

---

## SSL

Для лабораторного стенда используется самоподписанный wildcard-сертификат:

```
CN=*.diego.home
```

Создаётся автоматически при помощи OpenSSL.

Используются файлы:

```
/etc/ssl/private/nginx-wildcard.key
/etc/ssl/certs/nginx-wildcard.crt
```

---

## Reverse Proxy

Backend-серверы формируются динамически через шаблон Jinja2.

Пример итоговой конфигурации:

```nginx
upstream backend_servers {
    server 192.168.0.102:8000;
    server 192.168.0.150:8000;
}
```

---

## Балансировка

Используется стандартный алгоритм Nginx — **Round Robin**.

Проверка:

```bash
curl https://nginx.diego.home -k
```

Пример ответов:

```
Hello from LXC Docker (192.168.0.102)

Hello from CentOS VM (192.168.0.150)

Hello from LXC Docker (192.168.0.102)
```

---

## Запуск

```bash
ansible-playbook -i inventory.ini playbook.yml
```

---

## Проверка конфигурации

Перед перезапуском выполняется:

```bash
nginx -t
```

При ошибке в конфигурации Nginx не будет перезапущен.

---

## Используемые технологии

- Ansible
- Nginx
- OpenSSL
- Jinja2
- Python HTTP Server
