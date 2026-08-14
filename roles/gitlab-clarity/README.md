# GitLab Clarity — Ansible Role

## Назначение

Устанавливает и настраивает **GitLab CE** на VM `gitlab-clarity` (192.168.0.161) для проекта Clarity и связанных CI/CD задач.

## Архитектура

```
gitlab-clarity (192.168.0.161)
├── GitLab CE
├── Git repositories
├── встроенный Container Registry (порт 5050)
├── встроенный PostgreSQL
├── встроенный Redis
└── остальные GitLab Omnibus services (Sidekiq, Puma, Gitaly)
```

## Требования

- **Целевая ОС:** Ubuntu Server 24.04 LTS
- **Ansible:** >= 2.14
- **Коллекции:** `community.general` (для модуля `community.general.ufw`)

### Целевая VM

| Параметр       | Значение                     |
|----------------|------------------------------|
| Hostname       | gitlab-clarity               |
| Domain         | diego.home                   |
| FQDN           | gitlab-clarity.diego.home    |
| IP             | 192.168.0.161/24             |
| Gateway        | 192.168.0.1                  |
| DNS            | 192.168.0.103                |
| CPU            | 2 vCPU                       |
| RAM            | 4 GB                         |
| Disk           | 120 GB                       |

### Ресурсы

VM имеет 2 vCPU и 4 GB RAM. Роль применяет оптимизацию GitLab Omnibus для небольших инсталляций:

- Отключены: Prometheus, Alertmanager, node_exporter, redis_exporter, postgres_exporter, gitlab_exporter, GitLab KAS
- Puma: 2 worker processes
- Sidekiq: max_concurrency = 10

## Что устанавливается

- `gitlab-ce` из официального репозитория GitLab
- UFW (firewall) с минимальными правилами: SSH (22), HTTP (80), Registry (5050)

## Что НЕ устанавливается

- Docker / docker-compose / python3-docker
- GitLab Runner (любого типа)
- k3s / kubectl / Helm
- Kubernetes компоненты
- HTTPS / Let's Encrypt
- Внешний PostgreSQL или Redis
- Prometheus / Alertmanager / exporters

## Переменные (defaults/main.yml)

Все переменные имеют префикс `gitlab_clarity_` для предотвращения конфликтов со старой ролью `gitlab`.

| Переменная                              | По умолчанию                              | Описание                              |
|-----------------------------------------|-------------------------------------------|---------------------------------------|
| `gitlab_clarity_external_url`           | `http://gitlab-clarity.diego.home`        | Основной URL GitLab                   |
| `gitlab_clarity_registry_external_url`  | `http://gitlab-clarity.diego.home:5050`   | URL Container Registry                |
| `gitlab_clarity_package`                | `gitlab-ce`                               | Пакет GitLab                          |
| `gitlab_clarity_edition`                | `ce`                                      | Редакция GitLab                       |
| `gitlab_clarity_registry_enabled`       | `true`                                    | Включить Registry                     |
| `gitlab_clarity_letsencrypt_enabled`    | `false`                                   | Let's Encrypt (отключён)              |
| `gitlab_clarity_resource_optimization`  | `true`                                    | Оптимизация для 4 GB RAM              |
| `gitlab_clarity_puma_worker_processes`  | `2`                                       | Количество Puma workers               |
| `gitlab_clarity_sidekiq_max_concurrency`| `10`                                      | Макс. конкуренция Sidekiq             |
| `gitlab_clarity_manage_ufw`             | `true`                                    | Управлять UFW                         |
| `gitlab_clarity_ufw_allowed_ports`      | `[22, 80, 5050]`                          | Разрешённые порты                     |

## Пример inventory

```ini
[gitlab_clarity]
gitlab-clarity ansible_host=192.168.0.161
```

## Пример playbook

```yaml
---
- name: Configure GitLab Clarity
  hosts: gitlab_clarity
  become: true
  roles:
    - role: gitlab-clarity
```

## Запуск

```bash
# Проверка синтаксиса
ansible-playbook playbooks/gitlab-clarity.yml --syntax-check

# Запуск (check mode)
ansible-playbook playbooks/gitlab-clarity.yml --check

# Реальный запуск
ansible-playbook playbooks/gitlab-clarity.yml
```

## Проверки после установки

Роль автоматически проверяет:

1. **Установка пакета:** `dpkg -l | grep gitlab-ce`
2. **Статус сервисов:** `gitlab-ctl status`
3. **Health endpoint:** `http://gitlab-clarity.diego.home/-/health` (через `ansible.builtin.uri` с retry/delay/until)

## Ограничения 4 GB RAM

- Мониторинг (Prometheus, Alertmanager, exporters) отключён
- GitLab KAS отключён
- Puma ограничена 2 workers
- Sidekiq ограничен concurrency = 10
- Не рекомендуется для production-нагрузок

## HTTP / Registry

- На текущем этапе используется HTTP (закрытая лабораторная сеть)
- Registry работает на порту 5050 через встроенный GitLab Omnibus
- HTTPS и Let's Encrypt не настраиваются

## Kubernetes Runner

**GitLab Runner не входит в эту роль.**

Runner будет настроен **отдельным этапом** после завершения установки GitLab:

- Тип: Kubernetes executor
- Целевой кластер: существующий k3s (192.168.0.155–156)
- Ansible НЕ управляет k3s

## Лицензия

MIT

## Автор

Diego Home Lab
