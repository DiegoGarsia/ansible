# firewall role

## Описание

Роль `firewall` предназначена для настройки межсетевого экрана Linux с использованием **iptables**.

Конфигурация формируется автоматически на основе переменных Ansible и сохраняется в виде файла правил `/etc/iptables/rules.v4`, который затем применяется с помощью `iptables-restore`.

Подход позволяет:

- централизованно управлять правилами;
- легко расширять список сервисов;
- хранить конфигурацию в Git;
- получать полностью воспроизводимую конфигурацию на любом хосте.

---

## Возможности

- настройка политик INPUT/FORWARD/OUTPUT;
- разрешение локального интерфейса (`lo`);
- разрешение уже установленных соединений (`ESTABLISHED,RELATED`);
- описание сервисов через переменные;
- поддержка нескольких портов для одного сервиса;
- поддержка нескольких источников (`source`) для одного сервиса;
- применение одинаковых правил на всех управляемых узлах;
- автоматическое сохранение правил после перезагрузки системы.

---

## Структура роли

```
roles/
└── firewall
    ├── defaults/
    ├── handlers/
    ├── meta/
    ├── tasks/
    ├── templates/
    ├── vars/
    └── README.md
```

---

## Поддерживаемые платформы

- Ubuntu
- Debian
- CentOS Stream 9
- Rocky Linux 9
- AlmaLinux 9

---

## Используемые переменные

### group_vars/all.yml

```yaml
local_networks:
  - 192.168.0.0/24

jump_host_sources:
  - 192.168.0.100/32
```

### group_vars/managed.yml

```yaml
firewall_default_input_policy: DROP
firewall_default_forward_policy: DROP
firewall_default_output_policy: ACCEPT

firewall_default_sources: "{{ local_networks }}"

firewall_services:

  ssh:
    protocol: tcp
    ports:
      - 22
    sources: "{{ jump_host_sources }}"

  nginx:
    protocol: tcp
    ports:
      - 80
      - 443
    sources:
      - 0.0.0.0/0
```

---

## Добавление нового сервиса

Например, необходимо открыть Grafana.

```yaml
firewall_services:

  grafana:
    protocol: tcp
    ports:
      - 3000
```

Так как параметр `sources` отсутствует, будут использованы значения из

```yaml
firewall_default_sources
```

В приведенном примере доступ к Grafana получат только узлы локальной сети.

---

Если требуется открыть сервис только определённым узлам:

```yaml
firewall_services:

  postgres:
    protocol: tcp

    ports:
      - 5432

    sources:
      - 192.168.0.151/32
      - 192.168.0.152/32
      - 192.168.0.153/32
```

---

Если сервис необходимо открыть всем:

```yaml
firewall_services:

  nginx:
    protocol: tcp

    ports:
      - 80
      - 443

    sources:
      - 0.0.0.0/0
```

---

## Пример запуска

```bash
ansible-playbook playbooks/firewall.yml
```

---

## Проверка правил

Просмотр текущих правил:

```bash
sudo iptables -S
```

или

```bash
sudo iptables -L -n
```

Просмотр сохранённой конфигурации:

```bash
cat /etc/iptables/rules.v4
```

---

## Проверка доступа

Проверить доступ по SSH:

```bash
ssh user@host
```

Проверить HTTP:

```bash
curl http://host
```

Проверить доступность произвольного TCP-порта:

```bash
nc -vz host PORT
```

---

## Особенности реализации

Конфигурация генерируется шаблоном Jinja2.

После генерации создаётся файл:

```
/etc/iptables/rules.v4
```

После чего правила применяются командой:

```bash
iptables-restore /etc/iptables/rules.v4
```

Таким образом роль всегда работает с полной конфигурацией, а не добавляет отдельные правила по одному, что обеспечивает воспроизводимость и упрощает сопровождение.

---

## Пример результата

```text
*filter

:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

-A INPUT -p tcp -s 192.168.0.100/32 --dport 22 -j ACCEPT

-A INPUT -p tcp -s 0.0.0.0/0 --dport 80 -j ACCEPT
-A INPUT -p tcp -s 0.0.0.0/0 --dport 443 -j ACCEPT

COMMIT
```

---

## Лицензия

MIT
