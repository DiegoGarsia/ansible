# partoni role

Ansible роль для развёртывания высокодоступного PostgreSQL-кластера с использованием Patroni и etcd.

Проект создан в рамках лабораторной инфраструктуры для изучения:

- Ansible Roles;
- PostgreSQL High Availability;
- Patroni;
- потоковой репликации PostgreSQL;
- автоматического переключения Leader/Replica;
- работы распределённого хранилища состояния через etcd.

---

## Архитектура

В рамках лаборатории разворачивается кластер из двух PostgreSQL-узлов:

```
              +----------------+
              |      etcd      |
              |      DCS       |
              +--------+-------+
                       |
              Patroni cluster state
                       |
        +--------------+--------------+
        |                             |
        v                             v

  pg-node-02                     pg-node-03
  192.168.0.152                  192.168.0.153

  PostgreSQL                     PostgreSQL
  Patroni                        Patroni

  Leader                         Replica
  running                        streaming
```

---

## Компоненты

### PostgreSQL

Используется PostgreSQL 16.

Роль `postgres` отвечает за:

- установку PostgreSQL;
- создание обычного экземпляра PostgreSQL;
- создание пользователей и баз данных.

Эта роль не используется для управления Patroni-кластером.

---

### Patroni

Роль `patroni` отвечает за:

- установку Patroni;
- создание конфигурации Patroni;
- настройку взаимодействия с etcd;
- запуск Patroni через systemd;
- управление PostgreSQL-кластером.

Patroni использует отдельный каталог данных:

```
/var/lib/postgresql/patroni
```

Это позволяет отделить управляемый Patroni-кластер от обычного PostgreSQL экземпляра.

---

### etcd

В текущей реализации etcd устанавливается внутри роли Patroni.

etcd используется как DCS (Distributed Configuration Store), где Patroni хранит:

- информацию о Leader;
- состояние кластера;
- параметры конфигурации;
- информацию о членах кластера.

---

# Структура проекта

```
ansible/
|
├── inventory/
|
├── playbooks/
|
│   └── install_patroni.yml
|
├── roles/
|
│   ├── postgres/
│   |
│   ├── patroni/
│   |
│   └── backup/
|
└── ansible.cfg
```

---

# Переменные Patroni

Основные переменные находятся в:

```
roles/patroni/defaults/main.yml
```

Пример:

```yaml
patroni_scope: postgres

patroni_rest_port: 8008

patroni_data_dir: /var/lib/postgresql/patroni

patroni_postgres_version: 16

replication_user: replicator
```

---

# Конфигурация Patroni

Шаблон:

```
roles/patroni/templates/patroni.yml.j2
```

Генерирует конфигурацию:

```
/etc/patroni.yml
```

Пример основных параметров:

```yaml
scope: postgres

name: pg-node-02

etcd3:
  host: 192.168.0.151:2379

postgresql:
  listen: 0.0.0.0:5432
  data_dir: /var/lib/postgresql/patroni
```

---

# Установка

Запуск роли:

```bash
ansible-playbook -i inventory playbooks/install_patroni.yml
```

После выполнения на PostgreSQL узлах запускается Patroni:

```bash
systemctl status patroni
```

---

# Проверка состояния кластера

Проверка через Patroni:

```bash
patronictl -c /etc/patroni.yml list
```

Пример рабочего состояния:

```
+ Cluster: postgres +

Member       Role       State
--------------------------------
pg-node-02   Leader     running
pg-node-03   Replica    streaming
```

---

# Проверка потоковой репликации

На Leader:

```bash
sudo -u postgres psql \
-c "select client_addr,state,sync_state from pg_stat_replication;"
```

Ожидаемый результат:

```
 client_addr     state       sync_state
----------------------------------------
 192.168.0.153   streaming   async
```

---

# Проверка переключения ролей

Для проверки HA используется:

```bash
patronictl -c /etc/patroni.yml switchover
```

Пример:

До переключения:

```
pg-node-02  Leader
pg-node-03  Replica
```

После:

```
pg-node-03  Leader
pg-node-02  Replica
```

После обратного переключения:

```
pg-node-02  Leader
pg-node-03  Replica
```

---

# Особенности реализации

## Отдельный data directory

Patroni не использует стандартный PostgreSQL каталог:

```
/var/lib/postgresql/16/main
```

Созданный обычной ролью PostgreSQL.

Вместо этого используется:

```
/var/lib/postgresql/patroni
```

Такой подход позволяет Patroni самостоятельно:

- инициализировать кластер;
- создавать реплики;
- выполнять bootstrap;
- управлять состоянием PostgreSQL.

---

# Ограничения проекта

Проект является лабораторной реализацией.

Не предназначен для прямого использования в production без дополнительной настройки.

Отсутствуют:

- TLS для PostgreSQL и etcd;
- HAProxy/ProxySQL слой;
- автоматическое резервное копирование WAL;
- мониторинг;
- автоматическое тестирование роли через Molecule.

---

# Цель проекта

Основная цель — изучение построения PostgreSQL High Availability инфраструктуры с использованием:

- Ansible;
- PostgreSQL;
- Patroni;
- etcd;
- streaming replication.

---

# Проверенное состояние

На момент завершения лаборатории:

✅ Patroni кластер успешно создан  
✅ Leader выбран автоматически  
✅ Replica подключена через streaming replication  
✅ WAL replication работает  
✅ Lag = 0  
✅ Switchover выполнен успешно в обе стороны  
✅ PostgreSQL управляется Patroni
