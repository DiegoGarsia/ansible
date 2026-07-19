# postgres role

## Описание

Роль `postgres` предназначена для автоматизированной установки и базовой настройки PostgreSQL на Linux-серверах с использованием Ansible.

Роль выполняет полный первоначальный этап подготовки PostgreSQL:

- установка PostgreSQL и дополнительных расширений;
- проверка состояния PostgreSQL-кластера;
- создание отдельного пользователя базы данных;
- создание тестовой базы данных;
- загрузка демонстрационных данных;
- выполнение базовой валидации работоспособности.

Роль разработана с учетом дальнейшего расширения инфраструктуры и используется как базовый слой перед настройкой отказоустойчивого PostgreSQL-кластера через Patroni.

---

# Поддерживаемая платформа

Текущая реализация рассчитана на:

- Ubuntu 24.04 LTS
- PostgreSQL 16
- Ansible Core 2.16+

---

# Назначение роли

После выполнения роли сервер получает готовый экземпляр PostgreSQL:

```
PostgreSQL
 ├── пользователь приложения
 ├── тестовая база данных
 ├── загруженные таблицы и данные
 └── проверка состояния кластера
```

Пример подготовленной структуры:

```
Database:
    testdb

User:
    testuser

Tables:
    superheroes
    customers
    products
    orders
    sales
```

---

# Что делает роль

## 1. Установка PostgreSQL

Роль устанавливает:

- PostgreSQL server;
- PostgreSQL contrib modules.

Используется Ansible модуль:

```yaml
ansible.builtin.apt
```

Установка выполняется автоматически с учетом состояния системы.

---

## 2. Управление PostgreSQL cluster

Ubuntu использует механизм PostgreSQL Cluster через пакет `postgresql-common`.

Проверка выполняется не через:

```
systemctl status postgresql
```

так как данный сервис является мета-сервисом.

Вместо этого используется:

```bash
pg_lsclusters
```

Проверяется фактическое состояние экземпляра PostgreSQL.

Ожидаемый статус:

```
16 main 5432 online postgres
```

---

## 3. Создание пользователя PostgreSQL

Роль создает отдельного пользователя базы данных.

Пример:

```
username:
testuser
```

Пароль хранится через Ansible Vault.

Используется переменная:

```yaml
postgres_password
```

которая ссылается на зашифрованное значение:

```yaml
vault_postgres_password
```

Пример:

```yaml
postgres_password: "{{ vault_postgres_password }}"
```

---

## 4. Создание базы данных

Создается база:

```
testdb
```

Владельцем назначается созданный пользователь:

```
testuser
```

После выполнения:

```
testuser -> owner -> testdb
```

---

## 5. Импорт тестовых данных

Роль содержит SQL-дамп:

```
roles/postgres/files/sql_foundation.sql
```

Данный файл содержит:

- создание таблиц;
- заполнение тестовыми данными.

Перед импортом выполняется проверка наличия таблицы:

```
superheroes
```

Если таблица уже существует, повторный импорт не выполняется.

Это обеспечивает идемпотентность роли.

---

# Структура роли

```
postgres
├── defaults
│   └── main.yml
│
├── files
│   └── sql_foundation.sql
│
├── handlers
│   └── main.yml
│
├── tasks
│   ├── main.yml
│   ├── install.yml
│   ├── database.yml
│   ├── import.yml
│   └── verify.yml
│
├── vars
│   └── main.yml
│
└── README.md
```

---

# Основные задачи роли

## install.yml

Отвечает за:

- установку PostgreSQL;
- установку дополнительных пакетов;
- запуск PostgreSQL.

---

## database.yml

Отвечает за:

- создание PostgreSQL пользователя;
- создание базы данных;
- назначение владельца базы.

Использует коллекцию:

```
community.postgresql
```

---

## import.yml

Отвечает за:

- копирование SQL-файла;
- проверку существующих объектов;
- импорт демонстрационных данных.

---

## verify.yml

Выполняет проверку:

- существует ли PostgreSQL cluster;
- находится ли cluster в состоянии `online`.

---

# Переменные роли

Основные переменные находятся:

```
roles/postgres/defaults/main.yml
```

Пример:

```yaml
postgres_user: testuser

postgres_db: testdb

postgres_password: "{{ vault_postgres_password }}"
```

---

# Работа с Ansible Vault

Чувствительные данные не хранятся внутри роли.

Используется:

```
inventory/group_vars/vault.yml
```

Пример содержимого:

```yaml
vault_postgres_password: strongpassword
```

Файл должен быть зашифрован:

```bash
ansible-vault encrypt inventory/group_vars/vault.yml
```

---

# Использование роли

Пример playbook:

```yaml
- name: Install PostgreSQL
  hosts: postgres
  become: true

  roles:
    - postgres
```

Запуск:

```bash
ansible-playbook playbooks/install_postgres.yml
```

---

# Особенности реализации

## Идемпотентность

Роль можно запускать повторно.

Повторный запуск:

- не пересоздает пользователя;
- не пересоздает базу;
- не импортирует SQL повторно;
- не ломает существующую конфигурацию.

---

## Ограничение

На текущем этапе роль предназначена для подготовки PostgreSQL.

Она не выполняет:

- настройку streaming replication;
- настройку Patroni;
- управление failover;
- создание PostgreSQL HA-кластера.

Эти функции реализуются отдельными ролями:

```
etcd
patroni
```

---

# Использование в проекте

Роль является первым этапом подготовки PostgreSQL-инфраструктуры.

Текущая архитектура:

```
pg-node-01
    |
    | PostgreSQL
    | testdb
    | backup
    |
pg-node-02
    |
    | PostgreSQL
    |
pg-node-03
    |
    | PostgreSQL
```

Следующим этапом выполняется настройка отказоустойчивого PostgreSQL-кластера через Patroni.
