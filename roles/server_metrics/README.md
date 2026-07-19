# server_metrics role

Ansible-роль для установки сервиса сбора базовых метрик сервера.

Роль устанавливает Bash-скрипт, который собирает информацию о состоянии сервера, и настраивает запуск скрипта через `systemd service` и `systemd timer`.

Собранные метрики доступны через `journalctl`.

---

## Возможности

Роль выполняет следующие действия:

- устанавливает Bash-скрипт сбора метрик;
- создает systemd unit-файл сервиса;
- создает systemd timer для запуска каждые 5 минут;
- включает и запускает timer;
- отправляет вывод скрипта в systemd journal.

Собираемые метрики:

- Load Average (LA);
- свободное место на дисках;
- топ-5 процессов по потреблению оперативной памяти.

---

## Требования

- Ansible >= 2.12
- Linux с поддержкой systemd
- права `root` или возможность использования `become`

Поддерживаемые системы:

- Ubuntu
- Debian (с systemd)

---

## Структура роли

```
roles/server_metrics/
├── defaults/
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
├── templates/
│   ├── metrics.sh.j2
│   ├── my-service.service.j2
│   └── my-service.timer.j2
└── tests/
```

---

## Использование

### 1. Подключение роли в playbook

Пример `server_metrics.yml`:

```yaml
---
- name: Install server metrics collector
  hosts: managed
  become: true

  roles:
    - server_metrics
```

В данном примере роль применяется только к группе `managed`.

---

### 2. Запуск playbook

```bash
ansible-playbook -i inventory.ini server_metrics.yml
```

---

## Inventory пример

```ini
[jumphost]
jump ansible_host=10.0.0.10

[managed]
server1 ansible_host=10.0.0.11
server2 ansible_host=10.0.0.12
```

Jump host используется только для подключения и не получает настройки роли.

---

## Проверка работы

### Проверить состояние timer

```bash
systemctl status my-service.timer
```

Ожидаемый результат:

```
Active: active (waiting)
```

---

### Посмотреть расписание запуска

```bash
systemctl list-timers
```

Timer запускает сервис каждые 5 минут.

---

### Ручной запуск сервиса

Для проверки без ожидания таймера:

```bash
systemctl start my-service.service
```

---

### Просмотр логов

Вывод скрипта не записывается в отдельный файл.

Systemd автоматически сохраняет stdout/stderr сервиса в journald.

Просмотр логов:

```bash
journalctl -u my-service.service
```

Последние записи:

```bash
journalctl -u my-service.service -n 50
```

Просмотр логов в реальном времени:

```bash
journalctl -u my-service.service -f
```

---

## Пример вывода

```
===== Server metrics =====

Date: Sat Jul 18 12:00:01 UTC 2026

Load Average:
12:00:01 up 10 days, load average: 0.05, 0.10, 0.15

Disk usage:
Filesystem      Size  Used Avail Use%
/dev/sda1        40G   15G   25G  38%

Top 5 memory consuming processes:
USER       PID %MEM COMMAND
user      1234 12.5 firefox
root       321  8.1 dockerd

==========================
```

---

## Systemd компоненты

После установки создаются:

### Service

```
/etc/systemd/system/my-service.service
```

Отвечает за однократный запуск скрипта сбора метрик.

---

### Timer

```
/etc/systemd/system/my-service.timer
```

Запускает сервис каждые 5 минут.

---

### Скрипт

```
/usr/local/bin/metrics.sh
```

Содержит логику сбора метрик.

---

## Проверка после установки

Команды для диагностики:

```bash
systemctl status my-service.timer

systemctl status my-service.service

journalctl -u my-service.service

journalctl -xeu my-service.service
```

---

## Лицензия

MIT
