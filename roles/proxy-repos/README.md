# proxy-repos

Ansible-роль для **безопасной замены URL** репозиториев пакетных менеджеров APT (Debian/Ubuntu) и YUM/DNF (RedHat/CentOS/Rocky/AlmaLinux) на зеркало.

## Принцип безопасности

Роль выполняет **только точечную замену** одного URL на другой внутри существующих файлов источников. Она:

- ✅ **не удаляет** файлы (в т.ч. в `/etc/apt/sources.list.d/`);
- ✅ **не перезаписывает** конфигурационные файлы целиком;
- ✅ **не отключает** репозитории;
- ✅ **не выполняет** `apt upgrade` / `yum upgrade` (никакие пакеты не устанавливаются и не обновляются);
- ✅ сохраняет всё остальное содержимое файлов;
- ✅ создаёт резервную копию файла перед изменением (если включено).

## Требования

- Ansible >= 2.10
- Поддерживаемые семейства ОС:
  - **Debian** (Debian 11+ / Ubuntu 20.04+)
  - **RedHat** (CentOS 7+ / Rocky Linux 8+ / AlmaLinux 8+)

## Как использовать

URL зеркала задаётся **переменной** — достаточно изменить `proxy_repos_apt_mirror_to` (или `proxy_repos_yum_mirror_to`) при запуске роли. Значение можно передать через playbook, `group_vars`, `host_vars` или `--extra-vars`.

```bash
# Пример: замена на зеркало Яндекс через --extra-vars
ansible-playbook -i inventory playbooks/proxy-repos.yml \
  -e proxy_repos_apt_mirror_to=https://mirror.yandex.ru/ubuntu/
```

### Запуск на конкретной группе хостов

```bash
# Только на группе ubuntu_hosts
ansible-playbook -i inventory playbooks/proxy-repos.yml --limit ubuntu_hosts
```

## Структура роли

| Файл | Ответственность |
|---|---|
| [`defaults/main.yml`](defaults/main.yml) | Все переменные по умолчанию |
| [`tasks/main.yml`](tasks/main.yml) | Логика: сбор фактов, подключение OS-переменных, точечная замена URL |
| [`vars/Ubuntu.yml`](vars/Ubuntu.yml) | Список файлов APT для Ubuntu |
| [`vars/Debian.yml`](vars/Debian.yml) | Список файлов APT для Debian |
| [`vars/RedHat.yml`](vars/RedHat.yml) | Список файлов YUM/DNF для RedHat |
| [`vars/default.yml`](vars/default.yml) | Запасные значения для неизвестных ОС |
| [`handlers/main.yml`](handlers/main.yml) | Обновление кэша пакетов |
| [`meta/main.yml`](meta/main.yml) | Метаданные роли |

## Переменные роли

Все переменные определены в [`defaults/main.yml`](defaults/main.yml) и могут быть переопределены в playbook, group_vars или host_vars. OS-специфичные списки файлов находятся в [`vars/`](vars/) (`Debian.yml`, `Ubuntu.yml`, `RedHat.yml`).

### APT (Debian / Ubuntu)

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_apt_mirror_from` | Официальный URL, который заменяется | `http://archive.ubuntu.com/ubuntu` |
| `proxy_repos_apt_mirror_to` | Зеркало, на которое заменяется (передаётся как переменная) | `https://mirror.yandex.ru/ubuntu/` |
| `proxy_repos_apt_mirror_backup` | Создавать бэкап файла перед изменением | `true` |
| `proxy_repos_apt_mirror_files` | Список файлов для обработки (автоопределяется по ОС в `vars/`, можно переопределить) | `[]` |

> **OS-aware поведение:** роль сначала определяет дистрибутив/версию (`ansible_os_family`, `ansible_distribution`), затем выбирает целевые файлы из `proxy_repos_apt_mirror_files` (в `vars/Ubuntu.yml` и `vars/Debian.yml`). Каждый файл проверяется через `stat` — обрабатываются только существующие. Например, на Ubuntu 22.04+ в некоторых сценариях используется deb822-файл `/etc/apt/sources.list.d/ubuntu.sources`, а по умолчанию — классический `/etc/apt/sources.list`.

### YUM / DNF (RedHat family)

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_yum_mirror_from` | Официальный URL, который заменяется | `http://mirror.centos.org/centos` |
| `proxy_repos_yum_mirror_to` | Зеркало, на которое заменяется (передаётся как переменная) | `http://mirror.yandex.ru/centos/` |
| `proxy_repos_yum_mirror_backup` | Создавать бэкап файла перед изменением | `true` |
| `proxy_repos_yum_mirror_files` | Список файлов для обработки (автоопределяется по ОС в `vars/`, можно переопределить) | `[]` |

### Глобальные

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_update_cache` | Запускать `apt-get update` / `yum makecache` после изменений | `true` |

> `apt-get update` / `yum makecache` лишь обновляют индексы доступных пакетов и **не устанавливают и не обновляют** пакеты. При необходимости отключите через `proxy_repos_update_cache: false`.

## Пример playbook

```yaml
---
- name: Замена официального репозитория Ubuntu на зеркало
  hosts: ubuntu_hosts
  become: true
  vars:
    proxy_repos_apt_mirror_to: "https://mirror.yandex.ru/ubuntu/"
  roles:
    - role: proxy-repos

- name: Замена официального репозитория CentOS на зеркало
  hosts: rhel_hosts
  become: true
  vars:
    proxy_repos_yum_mirror_to: "http://mirror.yandex.ru/centos/"
  roles:
    - role: proxy-repos
```

## Пример результата

До применения (Ubuntu 24.04, `/etc/apt/sources.list`):

```
deb http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-security main restricted universe multiverse
```

После применения:

```
deb https://mirror.yandex.ru/ubuntu/ noble main restricted universe multiverse
deb https://mirror.yandex.ru/ubuntu/ noble-updates main restricted universe multiverse
deb https://mirror.yandex.ru/ubuntu/ noble-security main restricted universe multiverse
```

## Лицензия

MIT

## Автор

MTS DevOps
