# proxy-repos

Ansible-роль для замены конфигураций пакетных менеджеров APT (Debian/Ubuntu) и YUM/DNF (RedHat/CentOS/Rocky/AlmaLinux) на прокси-репозитории МТС.

## Требования

- Ansible >= 2.10
- Поддерживаемые семейства ОС:
  - **Debian** (Debian 11+ / Ubuntu 20.04+)
  - **RedHat** (CentOS 7+ / Rocky Linux 8+ / AlmaLinux 8+)

## Переменные роли

Все переменные определены в [`defaults/main.yml`](defaults/main.yml) и могут быть переопределены в playbook, group_vars или host_vars. OS-специфичные значения по умолчанию находятся в [`vars/`](vars/) (`Debian.yml`, `Ubuntu.yml`, `RedHat.yml`).

### APT (Debian / Ubuntu)

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_apt_base_url` | Базовый URL прокси-репозитория APT | `http://mts-apt-proxy.example.com/{{ ansible_distribution \| lower }}` |
| `proxy_repos_apt_distribution` | Кодовое имя дистрибутива (автоопределение) | `{{ ansible_distribution_release }}` |
| `proxy_repos_apt_suites` | Suites APT для генерации (добавьте `-updates`, `-security`, `-backports`, если они есть в прокси) | `["{{ proxy_repos_apt_distribution }}"]` |
| `proxy_repos_apt_components` | Компоненты репозитория | `main restricted universe multiverse` |
| `proxy_repos_apt_architectures` | Архитектуры для включения | `amd64` |
| `proxy_repos_apt_include_src` | Включать строки deb-src | `true` |
| `proxy_repos_apt_clean_sources_list_d` | Удалить все файлы в `/etc/apt/sources.list.d/` (**деструктивно**, см. предупреждение) | `false` |
| `proxy_repos_apt_sources_list_path` | Путь к основному файлу sources.list | `/etc/apt/sources.list` |

> **Предупреждение:** `proxy_repos_apt_clean_sources_list_d: true` удаляет **любые** файлы в `/etc/apt/sources.list.d/` (включая созданные другими ролями или вручную). Включайте только если прокси-репозиторий является единственным источником APT.

### YUM / DNF (RedHat family)

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_yum_base_url` | Базовый URL прокси-репозитория YUM | `http://mts-yum-proxy.example.com/{{ ansible_distribution \| lower }}/$releasever/$basearch/` |
| `proxy_repos_yum_gpgcheck` | Включить проверку GPG-подписи | `false` |
| `proxy_repos_yum_gpgkey` | URL GPG-ключа (опционально) | `""` |
| `proxy_repos_yum_enabled` | Репозиторий включён по умолчанию | `true` |
| `proxy_repos_yum_name` | Человекочитаемое имя репозитория | `MTS Proxy Repository` |
| `proxy_repos_yum_repo_id` | ID репозитория (секция в .repo / имя файла) | `mts-proxy` |
| `proxy_repos_yum_disable_default_repos` | Удалить стандартные репозитории (`baseos`, `appstream`, `base`, `updates`, `epel`) (**деструктивно**, см. предупреждение) | `false` |

> **Предупреждение:** `proxy_repos_yum_disable_default_repos: true` удаляет репозитории **по имени** и может не покрывать все дистрибутив-специфичные репозитории. Включайте только если прокси-репозиторий заменяет все стандартные репозитории.

### Глобальные

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `proxy_repos_update_cache` | Запускать `apt-get update` / `yum makecache` после изменений | `true` |

## Зависимости

Нет.

## Пример playbook

```yaml
---
- name: Настройка прокси-репозиториев APT на Debian/Ubuntu
  hosts: debian_hosts
  become: true
  vars:
    proxy_repos_apt_base_url: "http://mts-apt-proxy.internal.mts.ru/ubuntu"
    proxy_repos_apt_distribution: "jammy"
    proxy_repos_apt_suites:
      - "jammy"
      - "jammy-updates"
      - "jammy-security"
    proxy_repos_apt_components: "main universe"
  roles:
    - role: proxy-repos

- name: Настройка прокси-репозиториев YUM/DNF на RedHat-системах
  hosts: rhel_hosts
  become: true
  vars:
    proxy_repos_yum_base_url: "http://mts-yum-proxy.internal.mts.ru/rocky/$releasever/$basearch/"
    proxy_repos_yum_repo_id: "mts-proxy"
    proxy_repos_yum_name: "MTS Rocky Linux BaseOS"
  roles:
    - role: proxy-repos
```

## Лицензия

MIT

## Автор

MTS DevOps
