# Роль `gitlab`

Роль разворачивает на Ubuntu 24.04 GitLab Community Edition, встроенный GitLab Container Registry и GitLab Runner с Docker executor. Runner устанавливается и запускается как сервис `systemd`, затем регистрируется в GitLab по authentication token. В поставку также входит пример `.gitlab-ci.yml`, который собирает Docker-образ и публикует его в Registry.

> Расчётная конфигурация из задания — `gitlab.diego.home`, 2 vCPU, 8 ГБ RAM и 50 ГБ диска — подходит для небольшого тестового проекта. Для рабочего контура используйте HTTPS, резервные копии и больше ресурсов.

## Требования

- Управляемая ВМ: Ubuntu Server 24.04 LTS, доступ по SSH пользователем с `sudo`.
- На машине Ansible: `ansible-core >= 2.15`.
- Коллекция для UFW:

```bash
ansible-galaxy collection install -r role/gitlab/requirements.yml
```

- DNS-запись `gitlab.diego.home`, указывающая на ВМ.

## Быстрый запуск

Первый запуск выполняйте без токена Runner и без API-переменных: роль установит GitLab и сообщит, что регистрация пропущена. После первого входа в GitLab создайте project runner: **Settings → CI/CD → Runners → New project runner**. Выберите тег `docker`, затем сохраните выданный authentication token `glrt-...` в Ansible Vault.

```bash
ansible-vault create group_vars/gitlab/vault.yml
```

Содержимое Vault:

```yaml
vault_gitlab_runner_token: "glrt-ЗАМЕНИТЕ_НА_ВАШ_ТОКЕН"
vault_gitlab_api_token: "glpat-ЗАМЕНИТЕ_НА_ВАШ_ТОКЕН"
vault_application_secret: "длинный-случайный-секрет"
```

`vault_gitlab_api_token` нужен только если роль должна создавать переменные проекта через API. Токен создаётся в GitLab: **User settings → Access tokens**, scope `api`.

Создайте inventory и playbook (см. `examples/`) и выполните:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/gitlab.yml --ask-vault-pass
```

Первый запуск GitLab может занять 10–20 минут. После него откройте `http://gitlab.diego.home`, задайте пароль `root` и создайте проект. Затем внесите `vault_gitlab_runner_token` в Vault и повторите эту же команду: роль зарегистрирует Runner. Когда проект уже создан, можно также задать `gitlab_project_id`, API token и `gitlab_cicd_variables`, после чего ещё раз запустить playbook.

## Основные переменные

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `gitlab_external_url` | Внешний адрес GitLab | `http://gitlab.diego.home` |
| `gitlab_registry_external_url` | Адрес Container Registry | `http://gitlab.diego.home:5050` |
| `gitlab_runner_token` | Authentication token `glrt-...` | пусто |
| `gitlab_runner_tags` | Теги Runner | `docker,linux` |
| `gitlab_runner_privileged` | Нужен для Docker-in-Docker | `true` |
| `gitlab_manage_ufw` | Управлять UFW | `true` |
| `gitlab_cicd_variables` | Список CI/CD variables для Project API | `[]` |

Полный пример приведён в `examples/group_vars/gitlab.yml`.

## Pipeline

Скопируйте `files/gitlab-ci.yml.example` в корень репозитория проекта как `.gitlab-ci.yml`, при необходимости заменив домен в `--insecure-registry`. Pipeline запускается только для default branch, строит два тега (`SHA` и `latest`) и отправляет их в `$CI_REGISTRY_IMAGE`.

GitLab автоматически предоставляет pipeline переменные `CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_REGISTRY_USER` и `CI_REGISTRY_PASSWORD`. Пароль имеет срок жизни job и не надо создавать или хранить вручную.

## Безопасность

Не записывайте `glrt-`, `glpat-`, пароли и ключи в Git. Храните их в Ansible Vault, а секреты приложения — в GitLab **Settings → CI/CD → Variables**. Для секретов включайте `Masked` и `Protected`; для многострочных сертификатов используйте тип `File`.

Текущая конфигурация использует HTTP и поэтому добавляет Registry в Docker `insecure-registries`. Это приемлемо только для закрытой тестовой сети. Для HTTPS задайте оба URL с `https://`, настройте сертификат/Let's Encrypt и удалите insecure registry.
