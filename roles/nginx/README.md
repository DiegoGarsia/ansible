# nginx role

Роль предназначена для автоматизации развертывание инфраструктуры с использованием Ansible.

В рамках работы необходимо:

- развернуть два backend-сервера с Flask-приложением;
- настроить Nginx в качестве Reverse Proxy;
- реализовать балансировку нагрузки методом Round Robin;
- использовать HTTPS с самоподписанным wildcard-сертификатом;
- использовать DNS-имена вместо IP-адресов.

---

# Структура проекта

```
.
├── inventory
│   ├── hosts.ini
│   └── group_vars
├── roles
│   ├── flask_app
│   └── nginx
└── site.yml
```

---

# Используемые роли

## flask_app

Выполняет:

- установку Python;
- создание виртуального окружения Python;
- установку Flask;
- копирование приложения;
- создание systemd-сервиса;
- запуск Flask;
- открытие порта 8000 в firewalld (для RedHat-подобных систем).

---

## nginx

Выполняет:

- установку Nginx;
- копирование SSL-сертификата и приватного ключа;
- создание конфигурации Reverse Proxy;
- настройку HTTPS;
- настройку балансировки нагрузки методом Round Robin;
- запуск и проверку конфигурации Nginx.

---

# Используемые хосты

| Имя | Назначение |
|------|------------|
| jumphost | управляющий сервер |
| nginx | Reverse Proxy |
| docker | Backend №1 |
| centos | Backend №2 |

Все серверы используют внутренний DNS.

Пример записей:

```
nginx.diego.home
docker.diego.home
centos.diego.home
```

---

# Балансировка

Балансировка выполняется штатным алгоритмом Nginx — **Round Robin**.

Конфигурация upstream формируется автоматически из группы `backend`.

Пример:

```nginx
upstream backend_servers {
    server docker.diego.home:8000;
    server centos.diego.home:8000;
}
```

---

# HTTPS

Используется самоподписанный wildcard-сертификат:

```
*.diego.home
```

Сертификат хранится в роли `nginx/files` и копируется на сервер средствами Ansible.

---

# Запуск

Проверка синтаксиса:

```bash
ansible-playbook -i inventory/hosts.ini site.yml --syntax-check
```

Развертывание:

```bash
ansible-playbook -i inventory/hosts.ini site.yml
```

---

# Проверка

Проверить работу Flask:

```bash
curl http://docker.diego.home:8000
```

```bash
curl http://centos.diego.home:8000
```

Проверить HTTPS:

```bash
curl -k https://nginx.diego.home
```

Проверить балансировку:

```bash
for i in {1..10}; do
    curl -sk https://nginx.diego.home | grep Hostname
done
```

В результате должны поочередно отображаться backend-серверы:

```
Hostname: docker
Hostname: centos
Hostname: docker
Hostname: centos
```

---

# Используемые технологии

- Ansible
- Nginx
- Flask
- Python 3
- systemd
- firewalld
- HTTPS
- DNS

---

# Особенности реализации

- приложение Flask разворачивается автоматически;
- используется виртуальное окружение Python (`venv`);
- Nginx использует DNS-имена backend-серверов;
- сертификат не генерируется при каждом запуске, а хранится в роли;
- конфигурация Nginx проверяется перед перезапуском;
- роль Flask автоматически открывает порт 8000 в firewalld для RedHat-подобных систем.

---

# Автор

Diego
