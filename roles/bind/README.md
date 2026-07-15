# Ansible Role: Bootstrap

## Описание

Роль **bootstrap** предназначена для первоначальной подготовки нового сервера после установки операционной системы.

После выполнения роли сервер будет:

* обновлён до последних версий пакетов;
* иметь установленный пакет `sudo`;
* иметь пользователя `diego`;
* принимать SSH-подключения по ключу;
* запрещать вход пользователю `diego` по паролю;
* иметь права администратора (`sudo` или `wheel`);
* автоматически перезагружен.

---

# Структура проекта

```
ansible/
├── ansible.cfg
├── inventory
│   ├── hosts.ini
│   ├── group_vars
│   └── host_vars
├── playbooks
│   ├── bootstrap.yml
│   └── bind.yml
└── roles
    ├── bootstrap
    │   ├── defaults
    │   │   └── main.yml
    │   ├── files
    │   │   └── diego.pub
    │   ├── handlers
    │   │   └── main.yml
    │   ├── tasks
    │   │   └── main.yml
    │   └── README.md
    ├── bind
    └── qemu_guest_agent
```

---

# Требования

* Debian / Ubuntu или RedHat-совместимая ОС;
* Ansible 2.15+;
* SSH-доступ под пользователем `root`;
* публичный SSH-ключ пользователя расположен в:

```
roles/bootstrap/files/diego.pub
```

---

# Используемые группы Inventory

Роль выполняется для группы:

```ini
[managed:children]
lxc
kvm
```

Состав группы определяется в `inventory/hosts.ini`.

---

# Настраиваемые параметры

Файл:

```
roles/bootstrap/defaults/main.yml
```

```yaml
bootstrap_user: diego

bootstrap_shell: /bin/bash

bootstrap_create_home: true

bootstrap_lock_password: true

bootstrap_public_key: diego.pub

bootstrap_groups:
  Debian: sudo
  RedHat: wheel

bootstrap_reboot_timeout: 600
```

## Описание переменных

| Переменная                 | Назначение                                       |
| -------------------------- | ------------------------------------------------ |
| `bootstrap_user`           | Имя создаваемого пользователя                    |
| `bootstrap_shell`          | Командная оболочка пользователя                  |
| `bootstrap_create_home`    | Создать домашний каталог                         |
| `bootstrap_lock_password`  | Запретить вход по паролю                         |
| `bootstrap_public_key`     | Имя файла публичного SSH-ключа                   |
| `bootstrap_groups`         | Группа администраторов для различных семейств ОС |
| `bootstrap_reboot_timeout` | Максимальное время ожидания перезагрузки         |

---

# Выполняемые действия

Во время выполнения роль:

1. обновляет систему;
2. устанавливает пакет `sudo`;
3. создаёт пользователя;
4. устанавливает публичный SSH-ключ;
5. добавляет пользователя в группу администраторов;
6. блокирует вход по паролю;
7. выполняет перезагрузку сервера и ожидает восстановления SSH-соединения.

---

# Playbook

Запуск роли выполняется через playbook:

```bash
ansible-playbook playbooks/bootstrap.yml
```

---

# Проверка работы

Проверить доступность серверов:

```bash
ansible managed -m ping
```

Проверить синтаксис playbook:

```bash
ansible-playbook playbooks/bootstrap.yml --syntax-check
```

Пробный запуск без внесения изменений:

```bash
ansible-playbook playbooks/bootstrap.yml --check
```

Запустить роль:

```bash
ansible-playbook playbooks/bootstrap.yml
```

---

# Принцип работы

Роль предназначена для однократной подготовки новых серверов после установки операционной системы.

Все параметры роли вынесены в `defaults/main.yml`, что позволяет при необходимости изменять имя пользователя, используемый SSH-ключ, административную группу и другие настройки без изменения логики роли.

После выполнения bootstrap сервер готов к дальнейшему управлению средствами Ansible и выполнению остальных ролей проекта.

