# host_info role

## Описание

Роль **host_info** предназначена для вывода основной информации об удаленном хосте и проверки состояния системной службы.

В ходе выполнения роль выводит:

- имя хоста;
- операционную систему;
- версию операционной системы;
- версию ядра Linux;
- архитектуру системы;
- IP-адрес основного сетевого интерфейса;
- состояние службы SSH (`ssh` для Ubuntu и `sshd` для CentOS).

## Требования

- Ansible 2.16 или выше;
- Python на управляемых узлах;
- Сбор фактов (`gather_facts: true`).

## Структура роли

```
roles/
└── host_info/
    ├── defaults/
    ├── files/
    ├── handlers/
    ├── meta/
    ├── tasks/
    │   └── main.yml
    ├── templates/
    ├── tests/
    └── vars/
```

## Использование

Пример плейбука:

```yaml
---
- name: Show host information
  hosts: managed
  gather_facts: true

  roles:
    - host_info
```

Запуск:

```bash
ansible-playbook -i inventory/hosts.ini host_info.yml
```

## Пример вывода

```
TASK [host_info : Show host information]

ok: [nginx] => {
    "msg": [
        "Hostname: nginx",
        "OS: Ubuntu",
        "Version: 24.04",
        "Kernel: 6.8.0-31-generic",
        "Architecture: x86_64",
        "IP: 192.168.0.101"
    ]
}

TASK [host_info : Show service status]

ok: [nginx] => {
    "msg": "Service ssh status: running"
}

ok: [centos] => {
    "msg": "Service sshd status: running"
}
```

## Используемые модули

В роли используются стандартные модули Ansible:

- `ansible.builtin.service_facts`
- `ansible.builtin.set_fact`
- `ansible.builtin.debug`

## Автор

Diego

## Лицензия

MIT
