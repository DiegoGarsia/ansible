## Описание

Данная роль предназначена для установки и настройки **BIND9** в качестве основного DNS-сервера домашней лаборатории.

DNS-сервер обслуживает зону:

```
diego.home
```

и автоматически создает:

- прямую DNS-зону (Forward Zone);
- обратную DNS-зону (Reverse Zone).

Все DNS-записи генерируются автоматически на основании Ansible Inventory. Ручное редактирование файлов зон не требуется.

---

# Структура проекта

```
ansible/
├── ansible.cfg
├── inventory
│   ├── hosts.ini
│   ├── group_vars
│   │   └── all.yml
│   └── host_vars
├── playbooks
│   ├── bootstrap.yml
│   └── bind.yml
└── roles
    └── bind
        ├── defaults
        │   └── main.yml
        ├── handlers
        │   └── main.yml
        ├── tasks
        │   ├── install.yml
        │   ├── config.yml
        │   ├── zones.yml
        │   └── main.yml
        ├── templates
        │   ├── named.conf.options.j2
        │   ├── named.conf.local.j2
        │   ├── db.forward.j2
        │   └── db.reverse.j2
        └── README.md
```

---

# Требования

- Debian / Ubuntu
- Ansible 2.15+
- Пакет BIND9 доступен в репозиториях ОС

---

# Используемые группы Inventory

DNS-сервер должен входить в группу:

```ini
[dns_host]
dns ansible_host=192.168.0.103
```

Все остальные серверы должны находиться в группе `managed`:

```ini
[managed:children]
lxc
kvm
```

Именно эта группа используется для автоматического построения DNS-записей.

---

# Настраиваемые параметры

Файл:
```
inventory/group_vars/all.yml
```

```yaml
ansible_user: root

dns_domain: diego.home

dns_server: dns
dns_server_ip: 192.168.0.103

dns_network: 192.168.0
dns_reverse_zone: 0.168.192.in-addr.arpa

dns_forwarders:
  - 192.168.0.1
```

## Описание переменных

|Переменная|Назначение|
|---|---|
|`dns_domain`|DNS-зона|
|`dns_server`|Имя DNS-сервера|
|`dns_server_ip`|IP-адрес DNS-сервера|
|`dns_reverse_zone`|Имя обратной зоны|
|`dns_forwarders`|DNS-серверы для пересылки внешних запросов|

---

# Автоматическое создание DNS-записей

Все записи создаются автоматически на основании Inventory.

Например:

```ini
nginx ansible_host=192.168.0.101
docker ansible_host=192.168.0.102
gitlab ansible_host=192.168.0.154
master ansible_host=192.168.0.155
worker ansible_host=192.168.0.156
```

После выполнения роли будет автоматически создана прямая зона:

```
nginx       IN A    192.168.0.101
docker      IN A    192.168.0.102
gitlab      IN A    192.168.0.154
master      IN A    192.168.0.155
worker      IN A    192.168.0.156
```

И обратная зона:

```
101 IN PTR nginx.diego.home.
102 IN PTR docker.diego.home.
154 IN PTR gitlab.diego.home.
155 IN PTR master.diego.home.
156 IN PTR worker.diego.home.
```

Добавление нового хоста в Inventory автоматически приводит к появлению соответствующих записей при следующем запуске роли.

---

# Установка и настройка

Запуск роли выполняется через playbook:

```bash
ansible-playbook playbooks/bind.yml
```

Во время выполнения роль:

1. устанавливает пакеты BIND9;
2. включает и запускает сервис;
3. настраивает `named.conf.options`;
4. настраивает `named.conf.local`;
5. генерирует прямую зону;
6. генерирует обратную зону;
7. при необходимости перезапускает службу BIND9.

---

# Проверка работы

Проверка прямой зоны:

```bash
dig @192.168.0.103 nginx.diego.home
```

Проверка обратной зоны:

```bash
dig @192.168.0.103 -x 192.168.0.101
```

Просмотр SOA-записи:

```bash
dig @192.168.0.103 diego.home SOA
```

Просмотр NS-записи:

```bash
dig @192.168.0.103 diego.home NS
```

---

# Принцип работы

Inventory является единственным источником информации о хостах.

При добавлении нового сервера достаточно внести его в `inventory/hosts.ini`.

Дополнительные изменения в роли, шаблонах или файлах зон не требуются.

Это исключает дублирование данных и позволяет полностью управлять DNS-конфигурацией средствами Ansible.
