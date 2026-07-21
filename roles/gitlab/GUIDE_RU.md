# Руководство по роли GitLab

## Что делает роль

Роль выполняется на одной ВМ и в следующем порядке: открывает сетевые порты, устанавливает Docker, подключает официальный репозиторий GitLab, устанавливает GitLab CE, включает встроенный Container Registry, ждёт готовности GitLab, устанавливает GitLab Runner и включает его службу `gitlab-runner.service`. Если задан token, Runner регистрируется как Docker Runner. В конце роль при необходимости создаёт или обновляет переменные конкретного проекта через GitLab API.

GitLab и Runner на одной машине удобны для тестового стенда. Docker executor создаёт отдельный контейнер для каждой CI job. Режим `privileged` разрешён намеренно: он необходим сервису `docker:dind`, используемому примером pipeline. Это повышает уровень доверия к коду, который может запускать pipeline; не выдавайте этот Runner непроверенным проектам.

## Структура

```text
role/gitlab/
├── defaults/main.yml       # безопасные значения по умолчанию
├── tasks/                  # отдельные этапы установки
├── handlers/main.yml       # gitlab-ctl reconfigure и рестарт Docker
├── files/gitlab-ci.yml.example
├── examples/               # inventory, playbook и group vars
├── README.md                # быстрый старт
└── GUIDE_RU.md              # это руководство
```

Каркас соответствует результату `ansible-galaxy init role/gitlab`. В среде разработки утилита `ansible-galaxy` отсутствовала, поэтому файлы стандартного каркаса созданы эквивалентно вручную.

## Токены и переменные

Есть три разных класса секретов:

1. `gitlab_runner_token` — authentication token созданного Runner (`glrt-...`). Он позволяет привязать агент к GitLab и должен находиться только в Ansible Vault.
2. `gitlab_api_token` — personal/group/project access token с `api`. Нужен роли лишь для API-запросов, создающих CI/CD variables. Его тоже храните в Vault.
3. Секреты приложения (`DATABASE_PASSWORD`, ключи деплоя, API-токены) — GitLab CI/CD Variables. Они доступны job только во время выполнения.

`gitlab_cicd_variables` — список объектов. Роль сначала читает состояние переменной: отсутствующая создаётся (`POST`), изменившаяся обновляется (`PUT`), а совпадающая не трогается. Значения скрываются в логах Ansible с `no_log: true`.

```yaml
gitlab_project_id: "platform/demo"  # либо числовой ID проекта
gitlab_api_token: "{{ vault_gitlab_api_token }}"
gitlab_cicd_variables:
  - key: APP_SECRET
    value: "{{ vault_application_secret }}"
    masked: true
    protected: true
    variable_type: env_var
```

Для `masked` GitLab предъявляет ограничения к формату значения; если GitLab отклоняет значение, сгенерируйте секрет, который не содержит пробелов и перевода строк, либо используйте `variable_type: file` и отключите masking только при необходимости.

## HTTP, Registry и TLS

В исходных параметрах задан HTTP. Registry работает на порту 5050, а Docker на Runner и сервис `docker:dind` получают флаг `--insecure-registry=gitlab.diego.home:5050`. Без этого `docker push` откажется отправлять образ в HTTP Registry.

Для перевода на TLS:

1. Обеспечьте DNS и сертификат для `gitlab.diego.home`.
2. Установите `gitlab_external_url: https://gitlab.diego.home` и `gitlab_registry_external_url: https://gitlab.diego.home:5050`.
3. Настройте сертификаты GitLab Omnibus или Let's Encrypt, если сервер доступен извне.
4. Задайте `gitlab_docker_insecure_registries: []` и удалите строку `--insecure-registry` из pipeline.
5. Повторно выполните playbook.

## Проверки и типовые ошибки

Проверить службы:

```bash
sudo gitlab-ctl status
sudo systemctl status gitlab-runner docker
sudo gitlab-runner list
curl -fsS http://gitlab.diego.home/-/health
```

Если Runner ожидает задания, проверьте его теги: pipeline и Runner должны иметь общий тег `docker`; либо включите `gitlab_runner_run_untagged: true`. Если job не может подключиться к Docker, проверьте `privileged: true`, состояние `docker` и доступность `docker:dind`. Если `push` выдаёт ошибку HTTPS/HTTP, совпадение адреса Registry должно быть во всех трёх местах: GitLab config, Docker daemon и `.gitlab-ci.yml`.

После изменения `gitlab_external_url` или Registry роль запускает `gitlab-ctl reconfigure`; это не мгновенная операция. Повторный запуск без изменения входных переменных не меняет GitLab, Docker, firewall, Runner или CI/CD variables. Регистрация Runner пропускается, когда его описание уже найдено локально. Установка пакетов и обновление APT cache допускают сетевую проверку, но не меняют конфигурацию без необходимости.
