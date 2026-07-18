# postgres role

## Описание

Роль `postgres` предназначена для автоматического развертывания и первоначальной настройки сервера PostgreSQL на Ubuntu 24.04 LTS с использованием Ansible.

В рамках выполнения роли производится:

- установка PostgreSQL и необходимых зависимостей;
- создание пользователя базы данных;
- создание тестовой базы данных;
- импорт демонстрационной SQL-базы;
- проверка успешности установки PostgreSQL.

Роль является идемпотентной и соответствует рекомендациям Ansible по использованию специализированных модулей коллекции `community.postgresql`.

---

# Возможности

После выполнения роли сервер PostgreSQL полностью готов к работе.

Автоматически выполняются следующие действия:

- установка пакетов PostgreSQL;
- запуск и включение службы PostgreSQL;
- создание пользователя БД;
- создание базы данных;
- импорт демонстрационной базы данных;
- проверка работоспособности PostgreSQL.

---

# Структура роли

```
roles/postgres
├── defaults
│   └── main.yml
├── files
│   └── sql_foundation.sql
├── handlers
│   └── main.yml
├── meta
│   └── main.yml
├── tasks
│   ├── install.yml
│   ├── database.yml
│   ├── import.yml
│   ├── verify.yml
│   └── main.yml
├── vars
│   └── main.yml
└── README.md
```

---

# Последовательность выполнения

Роль состоит из нескольких независимых этапов.

## 1. Установка PostgreSQL

Файл:

```
roles/postgres/tasks/install.yml
```

На данном этапе выполняется:

- обновление кэша APT;
- установка PostgreSQL;
- установка PostgreSQL Contrib;
- установка python3-psycopg2;
- запуск службы PostgreSQL;
- включение автозапуска службы.

Используемые модули:

- ansible.builtin.apt
- ansible.builtin.systemd_service

---

## 2. Создание пользователя и базы данных

Файл:

```
roles/postgres/tasks/database.yml
```

На данном этапе используются специализированные модули коллекции Community PostgreSQL.

Создается пользователь:

```
testuser
```

Создается база данных:

```
testdb
```

Владелец базы автоматически назначается созданному пользователю.

Используемые модули:

- community.postgresql.postgresql_user
- community.postgresql.postgresql_db

---

## 3. Импорт демонстрационной базы

Файл:

```
roles/postgres/tasks/import.yml
```

Перед импортом выполняется проверка существования таблицы:

```
superheroes
```

Если таблица отсутствует, производится импорт SQL-файла.

Если таблица уже существует — импорт пропускается.

Это обеспечивает идемпотентность роли.

Используемые модули:

- ansible.builtin.copy
- community.postgresql.postgresql_query
- community.postgresql.postgresql_script
- ansible.builtin.file

---

## 4. Проверка работы PostgreSQL

Файл:

```
roles/postgres/tasks/verify.yml
```

После завершения установки производится проверка:

- служба PostgreSQL запущена;
- служба включена в автозагрузку.

При необходимости выполнение роли завершается ошибкой.

---

# Используемые переменные

Основные переменные находятся в:

```
roles/postgres/defaults/main.yml
```

| Переменная | Назначение |
|------------|------------|
| postgres_db | Имя базы данных |
| postgres_user | Пользователь PostgreSQL |
| postgres_password | Пароль пользователя |
| postgres_version | Версия PostgreSQL |

---

# Хранение пароля

Пароль пользователя базы данных **не хранится** внутри роли.

Используется Ansible Vault.

Файл:

```
inventory/group_vars/vault.yml
```

До шифрования файл имеет вид:

```yaml
vault_postgres_password: "strongpassword"
```

После создания файл шифруется командой:

```bash
ansible-vault encrypt inventory/group_vars/vault.yml
```

В роли пароль используется следующим образом:

```yaml
postgres_password: "{{ vault_postgres_password }}"
```

Таким образом секреты полностью отделены от логики роли.

---

# Используемые коллекции

Перед запуском роли необходимо установить коллекцию:

```bash
ansible-galaxy collection install community.postgresql
```

или использовать файл:

```
requirements.yml
```

---

# Проверка результата

После выполнения роли можно проверить работу PostgreSQL.

Проверить службу:

```bash
systemctl status postgresql
```

Подключиться к базе:

```bash
sudo -u postgres psql -d testdb
```

Просмотреть таблицы:

```sql
\dt
```

Проверить количество супергероев:

```sql
SELECT COUNT(*) FROM superheroes;
```

Ожидаемый результат:

```
7281
```

---

# Идемпотентность

Роль является полностью идемпотентной.

Повторный запуск playbook:

- не создает пользователя повторно;
- не создает базу данных повторно;
- не импортирует SQL-файл повторно;
- не изменяет уже настроенную систему.

Все изменения выполняются только при необходимости.

---

# Возможные ошибки

## Не установлена коллекция

Ошибка:

```
community.postgresql.postgresql_user not found
```

Решение:

```bash
ansible-galaxy collection install community.postgresql
```

---

## Не найден psycopg2

Ошибка подключения к PostgreSQL.

Решение:

Проверить наличие пакета:

```bash
python3-psycopg2
```

---

## Ошибка Vault

При запуске появляется сообщение:

```
Attempting to decrypt...
```

Необходимо использовать:

```bash
ansible-playbook --ask-vault-pass
```

или

```bash
ansible-playbook --vault-password-file
```

---

# Используемые Ansible-модули

В роли используются исключительно FQDN-модули.

- ansible.builtin.apt
- ansible.builtin.systemd_service
- ansible.builtin.copy
- ansible.builtin.file
- community.postgresql.postgresql_user
- community.postgresql.postgresql_db
- community.postgresql.postgresql_query
- community.postgresql.postgresql_script

---

# Дальнейшее развитие

Данная роль является базой для последующей настройки:

- потоковой репликации PostgreSQL;
- Patroni;
- ETCD;
- автоматического failover.

