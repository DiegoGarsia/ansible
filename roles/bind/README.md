# Bind Role

Роль предназначена для установки и настройки DNS-сервера **BIND9** на базе Ubuntu/Debian.

В результате выполнения роли автоматически:

- устанавливаются необходимые пакеты;
- настраивается BIND9;
- создаются прямая и обратная зоны;
- генерируются DNS-записи на основании inventory Ansible;
- проверяется корректность конфигурации перед применением;
- перезапускается служба только при изменении конфигурации.

---

# Требования

- Ubuntu 24.04 LTS / Debian 12+
- Ansible 2.16+
- установлен пакет `bind9`
- повышение привилегий (`become: true`)

---

# Используемые переменные

Все основные параметры определяются в `group_vars/all.yml`.

## Обязательные

| Переменная | Описание | Пример |
|------------|----------|--------|
| `dns_domain` | DNS-домен | `diego.home` |
| `dns_server` | Имя DNS-сервера | `dns` |
| `dns_server_ip` | IP DNS-сервера | `192.168.0.103` |
| `dns_reverse_zone` | Обратная зона | `0.168.192.in-addr.arpa` |
| `dns_forwarders` | Список DNS-forwarder | `192.168.0.1` |

Пример:

```yaml
ansible_user: diego
ansible_become: true
ansible_become_method: sudo

dns_domain: diego.home

dns_server: dns
dns_server_ip: 192.168.0.103

dns_reverse_zone: 0.168.192.in-addr.arpa

dns_forwarders:
  - 192.168.0.1
```

---

# Переменные по умолчанию

`defaults/main.yml`

```yaml
bind_packages:
  - bind9
  - bind9-utils
  - dnsutils

bind_service: bind9

dns_allowed_networks:
  - localhost
  - 192.168.0.0/24
```

---

# Inventory

Роль автоматически формирует DNS-записи для всех хостов, входящих в группу `dns_records`.

Пример:

```ini
[dns]
dns ansible_host=192.168.0.103

[dns_records]
dns ansible_host=192.168.0.103
docker ansible_host=192.168.0.104
pg-node-01 ansible_host=192.168.0.105
jumphost ansible_host=192.168.0.106
```

Для каждого хоста будут автоматически созданы:

- A-запись;
- PTR-запись.

---

# Структура роли

```
roles/
└── bind/
    ├── defaults/
    ├── handlers/
    ├── tasks/
    ├── templates/
    └── README.md
```

---

# Проверка конфигурации

Перед применением конфигурации выполняются проверки:

```
named-checkconf
```

Для зоны прямого просмотра:

```
named-checkzone <domain> /etc/bind/db.<domain>
```

Для обратной зоны:

```
named-checkzone <reverse-zone> /etc/bind/db.<reverse-zone>
```

Если обнаружена ошибка в шаблоне или зоне, выполнение playbook будет остановлено.

---

# Серийный номер зоны (SOA Serial)

В шаблонах используется следующая конструкция:

```jinja
{{ '%Y%m%d01' | strftime }}
```

Она формирует серийный номер зоны в формате:

```
YYYYMMDDNN
```

где:

- `YYYY` — год;
- `MM` — месяц;
- `DD` — день;
- `NN` — порядковый номер изменения зоны за текущий день.

Например:

```
2026071701
```

При повторном изменении зоны в тот же день номер версии необходимо увеличить:

```
2026071702
```

---

# Использование

```yaml
- hosts: dns
  become: true

  roles:
    - bind
```

Запуск:

```bash
ansible-playbook site.yml
```

---

# Проверка работы

После выполнения роли рекомендуется выполнить следующие проверки.

Проверка конфигурации:

```bash
sudo named-checkconf
```

Проверка прямой зоны:

```bash
sudo named-checkzone diego.home /etc/bind/db.diego.home
```

Проверка обратной зоны:

```bash
sudo named-checkzone 0.168.192.in-addr.arpa /etc/bind/db.0.168.192.in-addr.arpa
```

Проверка службы:

```bash
systemctl status bind9
```

Проверка DNS:

```bash
dig dns.diego.home
dig docker.diego.home
dig google.com
dig -x 192.168.0.103
```

---

# Особенности реализации

- используется модуль `template` для генерации конфигурации;
- все изменения проходят предварительную проверку;
- перезапуск службы выполняется только при изменении файлов;
- DNS-записи создаются автоматически на основе inventory;
- используются FQDN в SOA и NS-записях;
- шаблоны не содержат жестко заданных имен хостов.

---

# Особенности окружения

В лабораторной инфраструктуре используется следующая схема:

```
Клиенты
        │
        ▼
BIND (192.168.0.103)
        │
        ▼
Forwarders
        │
        ▼
Маршрутизатор (192.168.0.1)
        │
        ▼
Интернет
```

Все клиенты используют BIND в качестве основного DNS-сервера.

BIND обслуживает локальную зону `diego.home`, а запросы к внешним доменам пересылает на DNS-сервер маршрутизатора через механизм `forwarders`.

---

# Лицензия

MIT
