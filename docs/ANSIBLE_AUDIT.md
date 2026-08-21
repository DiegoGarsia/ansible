# Ansible Infrastructure Audit

**Date:** 2026-08-14  
**Auditor:** Roo (Ansible Auditor)  
**Project:** `/home/diego/lab/ansible`  
**Mode:** Read-only audit — no changes made.

---

## 1. Executive Summary

The project is a personal lab infrastructure Ansible repository with **14 roles**, **14 playbooks**, and **1 inventory** file. It manages approximately **12 hosts** across Proxmox (KVM + LXC) for a home lab environment.

### Overall Assessment

| Area | Rating |
|------|--------|
| Project Structure | ⚠️ Needs improvement |
| Idempotency | ⚠️ Several issues |
| Security | 🔴 Critical issues found |
| Documentation | ⚠️ Multiple discrepancies |
| Variables | ⚠️ Some issues |
| Vault Usage | ✅ Properly used for secrets |

### Critical Issues Found

1. **🔴 CRITICAL**: Hardcoded GitLab Runner authentication token in plaintext (`inventory/group_vars/gitlab_hosts.yml:7`)
2. **🔴 CRITICAL**: Private SSL key stored in Git repository (`roles/nginx/files/nginx-wildcard.key`)
3. **🔴 CRITICAL**: Harbor admin password exposed in documentation (`docs/roles/harbor/README.md:77`)
4. **🔴 HIGH**: `host_key_checking: False` in `ansible.cfg:5` — disables SSH host key verification
5. **🔴 HIGH**: etcd listens on `0.0.0.0:2379` without authentication
6. **🔴 HIGH**: Patroni REST API on `0.0.0.0:8008` without authentication
7. **🔴 HIGH**: PostgreSQL `pg_hba` allows `all all 0.0.0.0/0 md5`

---

## 2. Current Architecture

```
ansible/
├── ansible.cfg
├── requirements.yml
├── .gitignore
├── inventory/
│   ├── hosts.ini
│   └── group_vars/
│       ├── main.yml
│       ├── managed.yml
│       ├── gitlab_hosts.yml
│       └── vault.yml
├── playbooks/
│   ├── site.yml                  # Flask backends + Nginx
│   ├── bootstrap.yml             # Initial server setup
│   ├── firewall.yml              # iptables firewall
│   ├── bind.yml                  # BIND9 DNS
│   ├── nginx.yml                 # Nginx reverse proxy
│   ├── install_postgres.yml      # PostgreSQL + backups
│   ├── install_patroni.yml       # Patroni HA cluster
│   ├── docker.yml                # Docker + Flask container
│   ├── docker_compose.yml        # Docker Compose Flask app
│   ├── gitlab.yml                # GitLab CE + Runner
│   ├── harbor.yml                # Harbor registry
│   ├── host_info.yml             # Host info display
│   ├── server_metrics.yml        # Metrics collector
│   ├── disable_firewall.yml      # Disable firewalls (lab)
│   └── test_pass.yml             # Debug vault passwords
├── roles/
│   ├── bootstrap/                # Initial server setup
│   ├── firewall/                 # iptables rules
│   ├── bind/                     # BIND9 DNS server
│   ├── nginx/                    # Nginx reverse proxy
│   ├── postgres/                 # PostgreSQL installation
│   ├── patroni/                  # Patroni HA cluster
│   ├── backup/                   # PostgreSQL backups
│   ├── docker/                   # Docker + Flask container
│   ├── docker_compose/           # Docker Compose Flask app
│   ├── flask_app/                # Flask systemd service
│   ├── gitlab/                   # GitLab CE + Runner
│   ├── harbor/                   # Harbor registry
│   ├── host_info/                # Host info display
│   └── server_metrics/           # Metrics collector
└── docs/
    └── roles/                    # Documentation copies
```

---

## 3. Inventory Map

### Hosts

| Hostname | IP | Groups | OS |
|----------|----|--------|----|
| `proxmox` | 192.168.0.200 | `proxmox_host`, `dns_records` | Unknown |
| `jumphost` | 192.168.0.100 | `jump_host`, `dns_records`, `os_ubuntu` | Ubuntu |
| `nginx` | 192.168.0.101 | `lxc`, `dns_records`, `nginx_host`, `managed`, `os_ubuntu` | Ubuntu |
| `docker` | 192.168.0.102 | `lxc`, `dns_records`, `backend`, `managed`, `os_ubuntu`, `docker_hosts` | Ubuntu |
| `dns` | 192.168.0.103 | `lxc`, `dns_records`, `dns_host`, `managed`, `os_ubuntu` | Ubuntu |
| `centos` | 192.168.0.150 | `kvm`, `dns_records`, `backend`, `managed`, `os_centos` | CentOS |
| `pg-node-01` | 192.168.0.151 | `kvm`, `dns_records`, `postgres`, `etcd`, `managed`, `os_ubuntu` | Ubuntu |
| `pg-node-02` | 192.168.0.152 | `kvm`, `dns_records`, `postgres`, `patroni`, `managed`, `os_ubuntu` | Ubuntu |
| `pg-node-03` | 192.168.0.153 | `kvm`, `dns_records`, `postgres`, `patroni`, `managed`, `os_ubuntu` | Ubuntu |
| `gitlab` | 192.168.0.154 | `kvm`, `dns_records`, `gitlab_hosts`, `managed`, `os_ubuntu` | Ubuntu |
| `master` | 192.168.0.155 | `kvm`, `dns_records`, `kubernetes_master`, `managed`, `os_ubuntu` | Ubuntu |
| `worker` | 192.168.0.156 | `kvm`, `dns_records`, `kubernetes_workers`, `managed`, `os_ubuntu` | Ubuntu |

### Groups

| Group | Type | Members |
|-------|------|---------|
| `proxmox_host` | host | proxmox |
| `jump_host` | host | jumphost |
| `lxc` | host | nginx, docker, dns |
| `kvm` | host | centos, pg-node-01, pg-node-02, pg-node-03, gitlab, master, worker |
| `lxc_proxy` | host | proxy-docker (nginx IP) |
| `kvm_proxy` | host | proxy-centos (nginx IP) |
| `dns_host` | host | dns |
| `dns_records` | children | proxmox_host, jump_host, lxc, kvm |
| `nginx_host` | host | nginx |
| `backend` | host | docker, centos |
| `postgres` | host | pg-node-01, pg-node-02, pg-node-03 |
| `patroni` | host | pg-node-02, pg-node-03 |
| `etcd` | host | pg-node-01 |
| `gitlab_hosts` | host | gitlab |
| `kubernetes_master` | host | master |
| `kubernetes_workers` | host | worker |
| `kubernetes` | children | kubernetes_master, kubernetes_workers |
| `managed` | children | lxc, kvm |
| `os_ubuntu` | host | jumphost, nginx, docker, dns, pg-node-*, gitlab, master, worker |
| `os_centos` | host | centos |
| `docker_hosts` | host | docker |

### Inventory Issues

| Issue | Severity | Details |
|-------|----------|---------|
| `lxc_proxy` group has wrong IP | WARNING | `proxy-docker` points to nginx IP (192.168.0.101), not docker |
| `kvm_proxy` group has wrong IP | WARNING | `proxy-centos` points to nginx IP (192.168.0.101), not centos |
| `proxmox` host not in `managed` | INFO | Proxmox host is not managed by Ansible roles |
| `jumphost` not in `managed` | INFO | Jump host is not managed by Ansible roles |
| No `host_vars/` directory | INFO | No per-host variable overrides |
| No `group_vars/all.yml` | INFO | Docs reference `group_vars/all.yml` but it doesn't exist |

---

## 4. Playbook Map

| Playbook | Target | Roles | Purpose |
|----------|--------|-------|---------|
| `site.yml` | backend, nginx | flask_app, nginx | Deploy Flask backends + Nginx reverse proxy |
| `bootstrap.yml` | managed | bootstrap | Initial server setup |
| `firewall.yml` | managed | firewall | Configure iptables |
| `bind.yml` | dns_host | bind | Configure BIND9 DNS |
| `nginx.yml` | nginx_host | nginx | Configure Nginx reverse proxy |
| `install_postgres.yml` | postgres, pg-node-01 | postgres, backup | Install PostgreSQL + backups |
| `install_patroni.yml` | postgres | patroni | Install Patroni HA cluster |
| `docker.yml` | docker_hosts | docker | Install Docker + Flask container |
| `docker_compose.yml` | docker_hosts | docker_compose | Deploy Flask with Docker Compose |
| `gitlab.yml` | gitlab | gitlab | Deploy GitLab CE + Runner |
| `harbor.yml` | docker | harbor | Deploy Harbor registry |
| `host_info.yml` | managed | host_info | Display host information |
| `server_metrics.yml` | managed | server_metrics | Install metrics collector |
| `disable_firewall.yml` | managed | (inline tasks) | Disable all firewalls (lab) |
| `test_pass.yml` | postgres | (inline tasks) | Debug vault passwords |

### Playbook Issues

| Issue | Severity | Details |
|-------|----------|---------|
| `site.yml` uses `backend` group but `playbooks/nginx.yml` uses `nginx_host` | WARNING | Inconsistent group usage for same role |
| `install_postgres.yml` runs `postgres` role on all `postgres` group, but `backup` only on `pg-node-01` | INFO | Intentional, but backup should be on pg-node-01 only |
| `install_patroni.yml` runs on `postgres` group but patroni tasks filter by `patroni` group | WARNING | Runs on pg-node-01 too, but etcd tasks filter correctly |
| `harbor.yml` targets `docker` host | INFO | Harbor and Docker roles share the same host |
| `test_pass.yml` exposes vault passwords in debug output | 🔴 HIGH | Debugging playbook that prints secrets |
| `disable_firewall.yml` contradicts `firewall.yml` | WARNING | One playbook enables firewall, another disables it |

---

## 5. Role Map

| Role | Purpose | Key Tasks |
|------|---------|-----------|
| `bootstrap` | Initial server setup | Update system, install packages, create user, configure SSH, QEMU agent |
| `firewall` | iptables firewall | Install iptables-persistent, deploy rules template, enable persistence |
| `bind` | BIND9 DNS server | Install bind9, configure named.conf, create forward/reverse zones |
| `nginx` | Nginx reverse proxy | Install nginx, copy SSL certs, deploy reverse proxy config |
| `postgres` | PostgreSQL installation | Install PostgreSQL, create user/database, import demo data, verify |
| `patroni` | Patroni HA cluster | Install etcd, install Patroni, configure Patroni, manage services |
| `backup` | PostgreSQL backups | Create backup dir, deploy backup script, configure systemd timer |
| `docker` | Docker + Flask container | Install Docker, build Flask image, run container, cleanup old Flask service |
| `docker_compose` | Docker Compose Flask app | Install docker-compose plugin, prepare files, deploy compose, run |
| `flask_app` | Flask systemd service | Install Python, create venv, deploy Flask app, systemd service |
| `gitlab` | GitLab CE + Runner | Install GitLab, configure Registry, install Runner, register Runner |
| `harbor` | Harbor registry | Download/extract Harbor, configure Docker insecure registry, deploy, push image |
| `host_info` | Host info display | Gather facts, display OS/version/IP/service status |
| `server_metrics` | Metrics collector | Deploy metrics script, systemd service + timer |

---

## 6. Role Dependencies

### Dependency Map

```
TASK: PostgreSQL Setup
├── playbooks/install_postgres.yml
│   ├── roles/postgres
│   │   ├── Requires: community.postgresql collection
│   │   ├── Depends on: bootstrap (implicit — needs user/SSH setup)
│   │   └── Depends on: firewall (implicit — needs port 5432 open)
│   └── roles/backup
│       ├── Depends on: postgres (implicit — needs database to exist)
│       └── Depends on: systemd (implicit)

TASK: Patroni HA Cluster
├── playbooks/install_patroni.yml
│   └── roles/patroni
│       ├── Depends on: postgres (implicit — needs PostgreSQL installed)
│       ├── Depends on: bootstrap (implicit)
│       ├── Depends on: firewall (implicit — needs ports 2379, 8008, 5432)
│       └── NOTE: cleanup.yml stops PostgreSQL, removes cluster

TASK: Nginx Reverse Proxy
├── playbooks/site.yml (or nginx.yml)
│   ├── roles/flask_app (on backend hosts)
│   │   ├── Depends on: bootstrap (implicit)
│   │   └── Depends on: firewall (implicit — needs port 8000)
│   └── roles/nginx (on nginx host)
│       ├── Depends on: bootstrap (implicit)
│       ├── Depends on: bind (implicit — needs DNS resolution)
│       └── Depends on: flask_app (implicit — needs backends running)

TASK: Docker + Flask
├── playbooks/docker.yml
│   └── roles/docker
│       ├── Depends on: bootstrap (implicit)
│       └── NOTE: cleanup.yml disables flask.service (from flask_app role)

TASK: Docker Compose
├── playbooks/docker_compose.yml
│   └── roles/docker_compose
│       ├── Depends on: docker (implicit — needs Docker Engine)
│       └── Depends on: bootstrap (implicit)

TASK: GitLab
├── playbooks/gitlab.yml
│   └── roles/gitlab
│       ├── Depends on: bootstrap (implicit)
│       ├── Depends on: bind (implicit — needs DNS)
│       └── NOTE: Installs Docker internally

TASK: Harbor
├── playbooks/harbor.yml
│   └── roles/harbor
│       ├── Depends on: docker (implicit — needs Docker Engine)
│       ├── Depends on: bootstrap (implicit)
│       └── NOTE: Configures Docker insecure-registries (overwrites daemon.json)
```

### Dependency Issues

| Issue | Severity | Details |
|-------|----------|---------|
| No `meta/dependencies` declared in any role | WARNING | All dependencies are implicit, not declared |
| `patroni` role stops PostgreSQL but doesn't declare dependency on `postgres` | WARNING | `cleanup.yml` assumes PostgreSQL is installed |
| `docker` role disables `flask.service` but doesn't declare dependency on `flask_app` | WARNING | Implicit conflict between roles |
| `harbor` overwrites `/etc/docker/daemon.json` | 🔴 HIGH | Conflicts with `gitlab` role which also writes to this file |
| `docker_compose` assumes Docker Engine is installed | WARNING | No dependency on `docker` role declared |
| `backup` role assumes PostgreSQL is running | INFO | No dependency on `postgres` role declared |

---

## 7. Task → Implementation Matrix

| # | My Task | Status | Roles | Playbooks | Issues |
|---|---------|--------|-------|-----------|--------|
| 1 | **Local DNS (BIND)** | ✅ Implemented | `bind` | `bind.yml` | DNS zone serial number uses `strftime` which changes every day — breaks idempotency |
| 2 | **Nginx reverse proxy** | ✅ Implemented | `nginx`, `flask_app` | `site.yml`, `nginx.yml` | SSL key stored in Git; no upstream health checks; wildcard cert is self-signed |
| 3 | **Bash monitoring script** | ✅ Implemented | `server_metrics` | `server_metrics.yml` | Timer template uses `OnUnitActiveSec=5min` but docs say "every 5 minutes" — correct |
| 4 | **Firewall (iptables)** | ✅ Implemented | `firewall` | `firewall.yml` | SSH restricted to jumphost only (192.168.0.100); 80/443 open for nginx |
| 5 | **Ansible host info** | ✅ Implemented | `host_info` | `host_info.yml` | Simple debug output, no issues |
| 6 | **Basic server setup** | ✅ Implemented | `bootstrap` | `bootstrap.yml` | Passwordless sudo for admin user; SSH hardening done properly |
| 7 | **PostgreSQL + test data** | ✅ Implemented | `postgres`, `backup` | `install_postgres.yml` | Import idempotency issue (see below) |
| 8 | **PostgreSQL replication (Patroni)** | ✅ Implemented | `patroni` | `install_patroni.yml` | etcd single-node (SPOF); no authentication on etcd/Patroni API |

### Task Status Summary

| Status | Count |
|--------|-------|
| ✅ Fully implemented | 8/8 |
| ⚠️ Implemented with issues | 6/8 |
| ❌ Not implemented | 0/8 |

---

## 8. Idempotency Audit

### Role-by-Role Assessment

#### `bootstrap` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| `Upgrade Debian packages` | `apt upgrade: dist` | **FAIL** — `upgrade: dist` always reports "changed" even if no packages upgraded. Use `upgrade: safe` or add `changed_when` |
| `Upgrade RedHat packages` | `dnf name: "*" state: latest` | **FAIL** — Always reports changed. Use `update_only: true` (already set) but still reports changed |
| `Create administrator account` | `user` | **PASS** — Idempotent |
| `Install SSH key` | `authorized_key` | **PASS** — Idempotent |
| SSH hardening tasks | `lineinfile` | **PASS** — Idempotent with `regexp` |

#### `firewall` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All tasks | `template`, `file`, `systemd`, `copy` | **PASS** — All idempotent |
| `Restore iptables rules` handler | `command` with `changed_when: false` | **PASS** — Correctly marked as not changing |

#### `bind` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All config tasks | `template` with `validate` | **PASS** — Idempotent |
| Zone checks | `command` with `changed_when: false` | **PASS** — Correct |
| **DNS zone serial number** | `strftime` in template | **⚠️ WARNING** — Serial `{{ '%Y%m%d01' \| strftime }}` changes daily, causing template diff every day even if zone content unchanged |

#### `nginx` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All tasks | `package`, `file`, `copy`, `template`, `service` | **PASS** — All idempotent |
| Handler validates config | `command` with `changed_when: false` | **PASS** — Correct |

#### `postgres` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| Install packages | `apt` | **PASS** |
| Create user/database | `postgresql_user`, `postgresql_db` | **PASS** — Idempotent |
| **Import SQL script** | `postgresql_script` | **⚠️ WARNING** — The `import.yml` checks if `superheroes` table exists but the `Import SQL script` task (line 26) does NOT have a `when` condition based on the check result. The check registers `superheroes_table` but the import task runs unconditionally. The SQL script itself uses `DROP TABLE IF EXISTS` so it's safe, but it will re-import data every run |
| Remove temp SQL file | `file` | **PASS** |

#### `patroni` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| Install etcd | `get_url`, `unarchive`, `copy` with `when: not etcd_binary.stat.exists` | **PASS** — Good use of `creates`-like pattern |
| **Deploy Patroni config** | `template` | **PASS** — Idempotent |
| **Start Patroni** | `systemd_service state: started` | **⚠️ WARNING** — Every run will ensure Patroni is started, which is correct but `state: started` always reports changed if service was already running. Use `state: started` with `changed_when: false` or check first |
| **Debug variables** | `debug` | **⚠️ WARNING** — Debug task prints passwords to output (security concern, not idempotency) |

#### `backup` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All tasks | `file`, `template`, `systemd_service` | **PASS** — All idempotent |
| **Note:** `cron.yml` exists but is NOT imported in `main.yml` | — | **INFO** — Dead code, not used |

#### `docker` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| Install Docker | `apt`, `systemd` | **PASS** |
| Build image | `docker_image` | **PASS** — Idempotent |
| **Run container** | `docker_container` with `recreate: true` | **⚠️ WARNING** — `recreate: true` forces container recreation on every run, even if nothing changed. This causes unnecessary downtime |
| **Disable old Flask service** | `systemd` with `failed_when: false` | **PASS** — Graceful handling |

#### `docker_compose` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| **Install docker compose** | `get_url` with `force: true` | **⚠️ WARNING** — `force: true` downloads the binary on every run even if already present. Should use `force: false` |
| **Start flask application** | `docker_compose_v2` with `build: always` | **⚠️ WARNING** — `build: always` rebuilds images on every run, causing unnecessary rebuilds. Use `build: if_absent` or remove |

#### `flask_app` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| Create venv | `command` with `creates` | **PASS** — Correct use of `creates` |
| Install pip deps | `pip` | **PASS** — Idempotent |
| All other tasks | `package`, `file`, `copy`, `template`, `systemd` | **PASS** |

#### `gitlab` — ⚠️ WARNING

| Task | Module | Issue |
|------|--------|-------|
| Download installer | `get_url` with `force: false` | **PASS** |
| Add repository | `command` with `creates` | **PASS** |
| **Configure GitLab** | `blockinfile` | **PASS** — Idempotent with markers |
| **Register Runner** | `command` with `creates`-like check | **PASS** — Checks if runner already registered |
| **Reconfigure GitLab** handler | `command` with `changed_when` | **⚠️ WARNING** — `changed_when` checks for Chef output strings which may vary by version |
| **Restart GitLab** handler | `command` with `changed_when: true` | **⚠️ WARNING** — Always reports changed when triggered |

#### `harbor` — 🔴 FAIL

| Task | Module | Issue |
|------|--------|-------|
| **Download Harbor** | `get_url` (no `force` param) | **⚠️ WARNING** — Downloads every time (default `force: true`) |
| **Configure Docker insecure registry** | `copy` | **⚠️ WARNING** — Overwrites `/etc/docker/daemon.json` every run |
| **Restart Docker** | `service state: restarted` | **🔴 FAIL** — Restarts Docker on every run, even if config unchanged. Should use handler with `notify` |
| **Create Harbor config** | `copy` from template | **⚠️ WARNING** — Copies from template every run |
| **Configure hostname/port/password** | `lineinfile`, `replace` | **🔴 FAIL** — These tasks modify the config file every run even if values haven't changed. `lineinfile` with `regexp` will always report changed if the line exists |
| **Disable HTTPS** | `replace` | **🔴 FAIL** — Always reports changed |
| **Run Harbor prepare** | `command` | **🔴 FAIL** — No `changed_when` or `creates`. Runs every time |
| **Start Harbor** | `docker_compose_v2` | **PASS** — Idempotent |

#### `host_info` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All tasks | `service_facts`, `debug`, `set_fact` | **PASS** — Read-only, no changes |

#### `server_metrics` — ✅ PASS

| Task | Module | Issue |
|------|--------|-------|
| All tasks | `template`, `systemd` | **PASS** — All idempotent |

### Idempotency Summary

| Role | Status |
|------|--------|
| bootstrap | ⚠️ WARNING |
| firewall | ✅ PASS |
| bind | ✅ PASS (minor serial issue) |
| nginx | ✅ PASS |
| postgres | ⚠️ WARNING |
| patroni | ⚠️ WARNING |
| backup | ✅ PASS |
| docker | ⚠️ WARNING |
| docker_compose | ⚠️ WARNING |
| flask_app | ✅ PASS |
| gitlab | ⚠️ WARNING |
| harbor | 🔴 FAIL |
| host_info | ✅ PASS |
| server_metrics | ✅ PASS |

---

## 9. Variable Audit

### Variable Sources

| Source | Files |
|--------|-------|
| `defaults/` | Role defaults (lowest precedence) |
| `vars/` | Role vars |
| `group_vars/main.yml` | PostgreSQL passwords (references vault) |
| `group_vars/managed.yml` | Firewall configuration |
| `group_vars/gitlab_hosts.yml` | GitLab configuration |
| `group_vars/vault.yml` | Encrypted secrets |
| Playbook variables | None defined |

### Variable Issues

| Issue | Severity | Details |
|-------|----------|---------|
| `local_networks` referenced in docs but not defined | WARNING | `docs/roles/firewall/README.md` references `local_networks` but it's not in any actual variable file |
| `jump_host_sources` referenced in docs but not defined | WARNING | Same as above |
| `dns_allowed_networks` in docs but not in code | WARNING | `docs/roles/bind/README.md` references this variable but it doesn't exist in actual role |
| `backup_schedule` in docs but not in code | WARNING | `docs/roles/backup/README.md` references `backup_schedule` but actual code uses `backup_hour`/`backup_minute` |
| `harbor_admin_password` in defaults with placeholder | INFO | `roles/harbor/defaults/main.yml` doesn't define `harbor_admin_password` — it's hardcoded in docs as `Harbor12345` |
| `postgres_superuser_password` in `group_vars/main.yml` | INFO | Properly references vault |
| `replication_password` in `group_vars/main.yml` | INFO | Properly references vault |
| `bootstrap_packages` in defaults but tasks use hardcoded lists | WARNING | `roles/bootstrap/defaults/main.yml` defines `bootstrap_packages` but `packages.yml` uses hardcoded package lists instead of the variable |
| `ssh_service_name` in defaults but tasks use hardcoded check | INFO | `host_info` role uses `ansible_distribution` to determine SSH service name instead of using a variable |

### Precedence Issues

| Issue | Severity | Details |
|-------|----------|---------|
| `postgres_password` defined in `defaults/main.yml` AND `group_vars/main.yml` | INFO | `group_vars` takes precedence, so `defaults` value is never used. Not a bug but confusing |
| `gitlab_runner_token` in `defaults/main.yml` (empty) AND `group_vars/gitlab_hosts.yml` (hardcoded) | 🔴 CRITICAL | The hardcoded token in `group_vars` overrides the empty default |

---

## 10. Vault & Secrets Audit

### Vault Usage

| File | Status | Details |
|------|--------|---------|
| `inventory/group_vars/vault.yml` | ✅ Properly encrypted | AES256 encrypted vault file |
| `inventory/group_vars/main.yml` | ✅ Proper references | References vault variables for passwords |

### Secrets Found in Plaintext

#### 🔴 CRITICAL: GitLab Runner Token

```
SECRET FOUND:
  file: inventory/group_vars/gitlab_hosts.yml
  line: 7
  variable: gitlab_runner_token
  type: authentication token (glrt- format)
  value: glrt-rN4RSzN-Lcs_HS-gQTYIM286MQpwOjIKdDozCnU6Mw8.01.1717voo2m
  status: EXPOSED — hardcoded in plaintext, committed to Git
```

#### 🔴 CRITICAL: Private SSL Key

```
SECRET FOUND:
  file: roles/nginx/files/nginx-wildcard.key
  variable: (file content)
  type: RSA private key (2048-bit)
  status: EXPOSED — stored in Git repository
```

#### 🔴 CRITICAL: Harbor Admin Password in Documentation

```
SECRET FOUND:
  file: docs/roles/harbor/README.md
  line: 77
  variable: harbor_admin_password
  type: admin password
  value: "Harbor12345"
  status: EXPOSED — hardcoded in documentation
```

#### ⚠️ HIGH: Vault Password File Reference

```
SECRET FOUND:
  file: ansible.cfg
  line: 10
  variable: vault_password_file
  type: vault password file path
  path: ~/.ansible/vault_pass
  status: INFO — path reference only, but if this file exists, it's a single point of compromise
```

### Secrets Management Recommendations

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| GitLab token in plaintext | 🔴 CRITICAL | Move to vault.yml immediately, rotate the token |
| SSL private key in Git | 🔴 CRITICAL | Remove from Git, generate on first run or use ACME |
| Harbor password in docs | 🔴 CRITICAL | Remove from docs, use vault |
| `test_pass.yml` prints secrets | 🔴 HIGH | Remove or protect with `no_log: true` |

---

## 11. Security Audit

### 🔴 CRITICAL

| # | Issue | Location | Details |
|---|-------|----------|---------|
| C1 | GitLab Runner token in plaintext | `inventory/group_vars/gitlab_hosts.yml:7` | Authentication token exposed in Git |
| C2 | Private SSL key in Git | `roles/nginx/files/nginx-wildcard.key` | Anyone with repo access has the private key |
| C3 | Harbor admin password in docs | `docs/roles/harbor/README.md:77` | Default password documented |

### 🔴 HIGH

| # | Issue | Location | Details |
|---|-------|----------|---------|
| H1 | `host_key_checking = False` | `ansible.cfg:5` | Disables SSH host key verification — MITM vulnerability |
| H2 | etcd no authentication | `roles/patroni/templates/etcd.service.j2:14-15` | etcd listens on `0.0.0.0:2379` with no TLS/auth |
| H3 | Patroni REST API no auth | `roles/patroni/templates/patroni.yml.j2:8` | REST API on `0.0.0.0:8008` with no authentication |
| H4 | PostgreSQL wide open | `roles/patroni/defaults/main.yml:43` | `host all all 0.0.0.0/0 md5` — accepts connections from anywhere |
| H5 | Flask runs as root | `roles/flask_app/templates/flask.service.j2:7` | `User=root` — should run as unprivileged user |
| H6 | Docker insecure registries | `roles/gitlab/tasks/docker.yml:22`, `roles/harbor/tasks/docker.yml` | Both roles configure insecure registries |
| H7 | Harbor HTTP only | `roles/harbor/tasks/deploy.yml:28-38` | HTTPS explicitly disabled |
| H8 | Debug playbook exposes secrets | `playbooks/test_pass.yml` | Prints vault passwords to output |
| H9 | Patroni debug task prints passwords | `roles/patroni/tasks/configure.yml:2-7` | Debug task outputs passwords |

### ⚠️ MEDIUM

| # | Issue | Location | Details |
|---|-------|----------|---------|
| M1 | Passwordless sudo | `roles/bootstrap/templates/sudoers.j2` | `NOPASSWD: ALL` — no sudo password prompt |
| M2 | Docker privileged mode | `roles/gitlab/tasks/runner.yml:51` | `--docker-privileged=true` — container has elevated privileges |
| M3 | UFW not actually configured | `roles/gitlab/defaults/main.yml:11` | `gitlab_manage_ufw: true` but no UFW tasks in the role |
| M4 | Harbor admin default user | `roles/harbor/defaults/main.yml:9` | Uses `admin` account — no separate user |
| M5 | GitLab HTTP (no HTTPS) | `roles/gitlab/defaults/main.yml:3` | `http://` not `https://` |
| M6 | No SSL configuration options | `roles/nginx/defaults/main.yml` | No variables for SSL config — hardcoded cert paths |

### ℹ️ LOW

| # | Issue | Location | Details |
|---|-------|----------|---------|
| L1 | etcd single node | `inventory/hosts.ini:53-54` | Only pg-node-01 runs etcd — single point of failure |
| L2 | No Patroni watchdog | `roles/patroni/templates/patroni.yml.j2` | No `watchdog` configuration for split-brain prevention |
| L3 | No backup encryption | `roles/backup/templates/pg-backup.sh.j2` | Backups are plain SQL — no encryption at rest |
| L4 | No monitoring/alerts | — | No monitoring or alerting configured |
| L5 | `.gitignore` doesn't cover certs/keys | `.gitignore` | Only ignores `access_key.pub`, not the wildcard key |

---

## 12. Documentation Audit

### Documentation vs. Code Comparison

#### `docs/roles/bootstrap/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| Lists `qemu-guest-agent` in base packages | `packages.yml` does NOT install `qemu-guest-agent` — it's installed in `qemu.yml` only for KVM hosts | ⚠️ Minor |
| Mentions `files/` directory in structure | Role has `files/` but docs structure doesn't show it | ⚠️ Missing |
| Says role is "one-time" | Role can be re-run safely (idempotent) | ✅ Correct |

#### `docs/roles/firewall/README.md` — 🔴 Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| References `group_vars/all.yml` with `local_networks` and `jump_host_sources` | File `group_vars/all.yml` does NOT exist | 🔴 Missing |
| `firewall_default_forward_policy: DROP` in docs | Actual code has `ACCEPT` in `group_vars/managed.yml:3` | 🔴 Wrong |
| SSH sources use `jump_host_sources` in docs | Actual code uses hardcoded `192.168.0.100/32` in `managed.yml:16` | ⚠️ Different |
| Nginx sources `0.0.0.0/0` in docs | Actual code has no `sources` for nginx, uses `firewall_default_sources` | ⚠️ Different |
| Docs mention Debian support | `meta/main.yml` only lists Ubuntu and EL | ⚠️ Minor |

#### `docs/roles/bind/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| References `dns_allowed_networks` variable | Variable does not exist in any file | 🔴 Missing |
| References `group_vars/all.yml` | File does not exist | 🔴 Missing |
| Says variables in `group_vars/all.yml` | Variables are in `roles/bind/vars/main.yml` | ⚠️ Wrong location |
| Example inventory shows different IPs | Actual inventory has different IPs | ⚠️ Outdated example |

#### `docs/roles/nginx/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| References `site.yml` as main playbook | `site.yml` exists but `nginx.yml` is the dedicated playbook | ⚠️ Both exist |
| Says DNS names used instead of IPs | Template uses `hostvars[host].ansible_host` which resolves to IPs, not DNS names | 🔴 Wrong |
| Mentions `flask_app` role deploys on backends | `site.yml` does this, but `nginx.yml` only runs nginx role | ⚠️ Partial |

#### `docs/roles/postgres/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| Says import is idempotent (checks `superheroes` table) | Code checks table but import task runs unconditionally | 🔴 Wrong |
| Mentions `python3-psycopg2` in packages | Package is in `defaults/main.yml` | ✅ Correct |

#### `docs/roles/patroni/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| Title says "partoni" (typo) | — | 🔴 Typo in filename |
| Says `postgres` role is not used for Patroni | `install_patroni.yml` runs on `postgres` group but only `patroni` role | ✅ Correct |
| Says etcd is installed inside Patroni role | Correct | ✅ Correct |

#### `docs/roles/backup/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| References `backup_schedule` variable | Actual code uses `backup_hour` and `backup_minute` | 🔴 Wrong |
| Uses ```` instead of ` ``` ` in YAML example | Formatting issue | ⚠️ Minor |

#### `docs/roles/docker/README.md` — ✅ Correct

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| All claims match code | — | ✅ Correct |

#### `docs/roles/docker_compose/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| Says role is idempotent | `get_url` with `force: true` and `build: always` break idempotency | 🔴 Wrong |
| References `vars/main.yml` for variables | Correct | ✅ Correct |

#### `docs/roles/flask_app/README.md` — ✅ Correct

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| All claims match code | — | ✅ Correct |

#### `docs/roles/gitlab/README.md` — ⚠️ Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| References `group_vars/gitlab/vault.yml` | File doesn't exist — vault is in `group_vars/vault.yml` | 🔴 Wrong path |
| References `requirements.yml` in role directory | File exists at `roles/gitlab/requirements.yml` | ✅ Correct |
| Says UFW is managed | `gitlab_manage_ufw: true` but no UFW tasks in role | 🔴 Not implemented |

#### `docs/roles/harbor/README.md` — 🔴 Discrepancies

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| Hardcodes `harbor_admin_password: "Harbor12345"` | Variable not in defaults — only in docs | 🔴 Security issue |
| Says role authorizes in Harbor | No `docker login` task exists | 🔴 Missing |
| Says checks artifacts via Harbor API | No such task exists | 🔴 Missing |

#### `docs/roles/host_info/README.md` — ✅ Correct

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| All claims match code | — | ✅ Correct |

#### `docs/roles/server_metrics/README.md` — ✅ Correct

| Claim in Docs | Actual Code | Status |
|---------------|-------------|--------|
| All claims match code | — | ✅ Correct |

---

## 13. Architecture Problems

### P1 — Role Duplication

| Roles | Problem |
|-------|---------|
| `docker` + `docker_compose` | Both deploy Flask apps using Docker. `docker` builds and runs a single container. `docker_compose` uses Compose for multi-container. They could be merged or one should depend on the other |
| `docker` + `flask_app` | Both deploy Flask apps. `docker` even disables `flask.service` (from `flask_app` role) in its cleanup. These are conflicting approaches on the same host |
| `gitlab` installs Docker internally | `gitlab` role installs Docker Engine even though `docker` role exists separately. Docker installation is duplicated |

### P2 — Missing Role Dependencies

No role declares `meta/dependencies`. All dependencies are implicit:

- `patroni` needs `postgres` (stops PostgreSQL in cleanup)
- `backup` needs `postgres`
- `docker_compose` needs `docker`
- `harbor` needs `docker`
- `flask_app` needs `bootstrap`

### P3 — Playbook Organization

- `site.yml` combines Flask backend + Nginx, but separate playbooks exist for each
- `install_postgres.yml` combines postgres + backup, but backup only runs on pg-node-01
- No `site.yml` that runs the full stack in order

### P4 — Inventory Structure

- `lxc_proxy` and `kvm_proxy` groups have incorrect IPs (both point to nginx)
- No `host_vars/` directory for per-host overrides
- `proxmox_host` and `jump_host` are not in `managed` group

### P5 — Dead Code

- `roles/backup/tasks/cron.yml` exists but is never imported
- `roles/patroni/templates/etcd.conf.yml.j2` exists but is never used (etcd is configured via command-line args in service template)

---

## 14. Technical Debt

| Item | Impact | Effort to Fix |
|------|--------|---------------|
| SSL private key in Git | Anyone with repo access has the key | 🔴 High — generate on first run |
| Hardcoded GitLab token | Token must be rotated, all runners re-registered | 🔴 High |
| Harbor idempotency issues | Every run restarts Docker, re-runs prepare | 🟡 Medium |
| No role dependencies declared | Unclear execution order, potential conflicts | 🟡 Medium |
| Docker daemon.json conflicts | GitLab and Harbor both overwrite this file | 🟡 Medium |
| Documentation out of sync | Misleading for new users | 🟡 Medium |
| Dead code (cron.yml, etcd.conf.yml.j2) | Confusing, unused files | 🟢 Low |
| Backup cron task not imported | Feature exists but unused | 🟢 Low |
| Typo in patroni docs filename | `partoni` instead of `patroni` | 🟢 Low |

---

## 15. Recommended Changes

### P0 — Must Fix Immediately

| # | Change | Reason | File(s) |
|---|--------|--------|---------|
| 0.1 | **Rotate and move GitLab token to Vault** | 🔴 CRITICAL — exposed token | `inventory/group_vars/gitlab_hosts.yml` → `vault.yml` |
| 0.2 | **Remove private SSL key from Git** | 🔴 CRITICAL — exposed private key | `roles/nginx/files/nginx-wildcard.key` |
| 0.3 | **Remove Harbor password from docs** | 🔴 CRITICAL — exposed password | `docs/roles/harbor/README.md` |
| 0.4 | **Enable host key checking** | 🔴 HIGH — MITM vulnerability | `ansible.cfg` |
| 0.5 | **Remove or protect `test_pass.yml`** | 🔴 HIGH — exposes vault secrets | `playbooks/test_pass.yml` |

### P1 — Should Fix Now

| # | Change | Reason | File(s) |
|---|--------|--------|---------|
| 1.1 | Add `changed_when` to apt upgrade tasks | Idempotency | `roles/bootstrap/tasks/update.yml` |
| 1.2 | Fix Harbor idempotency (use handlers, not direct restart) | Every run restarts Docker | `roles/harbor/tasks/docker.yml` |
| 1.3 | Fix `docker_container` — remove `recreate: true` or use comparison | Unnecessary container recreation | `roles/docker/tasks/run.yml` |
| 1.4 | Fix `docker_compose` — use `force: false` and `build: if_absent` | Unnecessary downloads/rebuilds | `roles/docker_compose/tasks/install.yml`, `run.yml` |
| 1.5 | Fix PostgreSQL import idempotency | Re-imports data every run | `roles/postgres/tasks/import.yml` |
| 1.6 | Add authentication to etcd and Patroni API | Security | `roles/patroni/templates/` |
| 1.7 | Restrict PostgreSQL `pg_hba` to specific hosts | Security | `roles/patroni/defaults/main.yml` |
| 1.8 | Fix `docs/roles/firewall/README.md` to match actual code | Documentation accuracy | `docs/roles/firewall/README.md` |
| 1.9 | Fix `docs/roles/bind/README.md` variable references | Documentation accuracy | `docs/roles/bind/README.md` |
| 1.10 | Fix `docs/roles/backup/README.md` variable names | Documentation accuracy | `docs/roles/backup/README.md` |

### P2 — Can Do Later

| # | Change | Reason | File(s) |
|---|--------|--------|---------|
| 2.1 | Add `meta/dependencies` to all roles | Explicit dependency management | All `roles/*/meta/main.yml` |
| 2.2 | Merge or clarify `docker` vs `docker_compose` vs `flask_app` roles | Role duplication | Multiple roles |
| 2.3 | Fix inventory `lxc_proxy` and `kvm_proxy` IPs | Correctness | `inventory/hosts.ini` |
| 2.4 | Create `group_vars/all.yml` for shared variables | Consistency | `inventory/group_vars/` |
| 2.5 | Add `no_log: true` to sensitive tasks | Security | `roles/patroni/tasks/configure.yml` |
| 2.6 | Fix DNS zone serial to not change every day | Idempotency | `roles/bind/templates/` |
| 2.7 | Remove dead code (`cron.yml`, `etcd.conf.yml.j2`) | Cleanup | `roles/backup/tasks/cron.yml`, `roles/patroni/templates/etcd.conf.yml.j2` |
| 2.8 | Run Flask as non-root user | Security | `roles/flask_app/templates/flask.service.j2` |
| 2.9 | Add backup encryption | Security | `roles/backup/templates/pg-backup.sh.j2` |

### P3 — Cosmetic

| # | Change | Reason | File(s) |
|---|--------|--------|---------|
| 3.1 | Fix typo "partoni" → "patroni" in docs filename | Cleanup | `docs/roles/patroni/README.md` |
| 3.2 | Add `.gitignore` entries for certs/keys | Safety | `.gitignore` |
| 3.3 | Update example IPs in documentation to match actual inventory | Consistency | Various docs |
| 3.4 | Fix markdown formatting in `docs/roles/backup/README.md` | Cleanup | `docs/roles/backup/README.md` |

---

## 16. Proposed Target Architecture

```
ansible/
├── ansible.cfg                    # Enable host_key_checking
├── requirements.yml               # Add community.docker, community.general
├── .gitignore                     # Add *.key, *.crt, vault_pass
│
├── inventory/
│   ├── hosts.ini                  # Fix proxy group IPs
│   ├── host_vars/                 # NEW — per-host variables
│   │   └── pg-node-01.yml
│   ├── group_vars/
│   │   ├── all.yml                # NEW — shared variables
│   │   ├── managed.yml
│   │   ├── gitlab_hosts.yml       # Remove hardcoded token
│   │   └── vault.yml              # All secrets here
│
├── playbooks/
│   ├── site.yml                   # Full-stack deployment
│   ├── bootstrap.yml
│   ├── security/
│   │   ├── firewall.yml
│   │   └── ssh_hardening.yml      # NEW — separate SSH hardening
│   ├── dns/
│   │   └── bind.yml
│   ├── proxy/
│   │   └── nginx.yml
│   ├── database/
│   │   ├── postgres.yml           # Combined postgres + backup
│   │   └── patroni.yml
│   ├── containers/
│   │   ├── docker.yml             # Docker Engine only
│   │   ├── docker_compose.yml     # Compose deployment
│   │   └── harbor.yml
│   ├── applications/
│   │   ├── gitlab.yml
│   │   └── flask_app.yml
│   ├── monitoring/
│   │   ├── host_info.yml
│   │   └── server_metrics.yml
│   └── utils/
│       └── disable_firewall.yml
│
├── roles/
│   ├── bootstrap/                 # Keep as-is, fix idempotency
│   ├── firewall/                  # Keep as-is
│   ├── bind/                      # Fix serial number
│   ├── nginx/                     # Generate cert on first run
│   ├── postgres/                  # Fix import idempotency
│   ├── patroni/                   # Add etcd/Patroni auth
│   ├── backup/                    # Remove dead cron.yml
│   ├── docker/                    # Docker Engine only (remove app)
│   ├── docker_compose/            # Fix force:true, build:always
│   ├── flask_app/                 # Run as non-root user
│   ├── gitlab/                    # Add UFW tasks, fix vault path
│   ├── harbor/                    # Fix idempotency, add docker login
│   ├── host_info/                 # Keep as-is
│   └── server_metrics/            # Keep as-is
│
└── docs/
    ├── ANSIBLE_AUDIT.md           # This file
    └── roles/                     # Update to match actual code
```

### Key Architectural Changes

1. **Separate Docker Engine installation from application deployment** — `docker` role should only install Docker Engine. Application deployment should be in `docker_compose` or separate roles
2. **Add `meta/dependencies`** — Every role should declare its dependencies explicitly
3. **Consolidate Flask deployment** — Choose one approach: `flask_app` (systemd), `docker` (single container), or `docker_compose` (multi-container). Currently all three exist and conflict
4. **Fix inventory groups** — Correct `lxc_proxy` and `kvm_proxy` IPs
5. **Add `host_vars/`** — For per-host configuration (e.g., etcd node IP)
6. **Create `group_vars/all.yml`** — For truly shared variables like `local_networks`

---

## 17. Verification Plan

### After Implementing Fixes

#### 1. Syntax Check
```bash
ansible-playbook --syntax-check playbooks/*.yml
```

#### 2. Lint
```bash
ansible-lint playbooks/*.yml roles/*/
```

#### 3. Dry-Run / Check Mode
```bash
ansible-playbook -i inventory/hosts.ini playbooks/bootstrap.yml --check --diff
ansible-playbook -i inventory/hosts.ini playbooks/firewall.yml --check --diff
ansible-playbook -i inventory/hosts.ini playbooks/nginx.yml --check --diff
ansible-playbook -i inventory/hosts.ini playbooks/bind.yml --check --diff
ansible-playbook -i inventory/hosts.ini playbooks/install_postgres.yml --check --diff
ansible-playbook -i inventory/hosts.ini playbooks/install_patroni.yml --check --diff
```

#### 4. Idempotency Test (Second Run Should Show No Changes)
```bash
ansible-playbook -i inventory/hosts.ini playbooks/bootstrap.yml
ansible-playbook -i inventory/hosts.ini playbooks/bootstrap.yml  # Second run — expect "ok=0 changed=0"
```

#### 5. Vault Verification
```bash
# Verify vault file is properly encrypted
ansible-vault view inventory/group_vars/vault.yml

# Verify no plaintext secrets in group_vars
grep -rn "glrt-\|glpat-\|BEGIN PRIVATE KEY" inventory/group_vars/ --include="*.yml"
```

#### 6. Security Scan
```bash
# Check for hardcoded secrets
grep -rn "glrt-\|glpat-\|BEGIN PRIVATE KEY\|BEGIN CERTIFICATE" roles/ --include="*.yml" --include="*.j2"
grep -rn "password:\|secret:\|token:" roles/ --include="*.yml" --include="*.j2" | grep -v "vault_\|{{"

# Check for no_log missing
grep -rn "password:\|token:" roles/ --include="*.yml" --include="*.j2" | grep -v "no_log\|vault_\|{{"
```

#### 7. Service Verification (Post-Deployment)
```bash
# Check services
systemctl status nginx
systemctl status patroni
systemctl status postgresql
systemctl status docker
systemctl status my-service.timer
systemctl status pg-backup.timer

# Check firewall
sudo iptables -L -n

# Check DNS
dig @192.168.0.103 diego.home

# Check Patroni cluster
patronictl -c /etc/patroni.yml list

# Check backups
ls -la /var/backups/pg/
```

#### 8. Documentation Verification
```bash
# Verify docs match code for each role
diff <(grep -h "variable:" docs/roles/*/README.md) <(grep -h "^[a-z_]" roles/*/defaults/main.yml)
```

---

## Appendix A: File Inventory

### Configuration Files
- `ansible.cfg` — Ansible configuration
- `requirements.yml` — Collection requirements
- `.gitignore` — Git ignore rules

### Inventory
- `inventory/hosts.ini` — Host definitions and groups
- `inventory/group_vars/main.yml` — PostgreSQL password references
- `inventory/group_vars/managed.yml` — Firewall configuration
- `inventory/group_vars/gitlab_hosts.yml` — GitLab configuration (contains hardcoded token)
- `inventory/group_vars/vault.yml` — Encrypted secrets

### Playbooks (14)
- `playbooks/site.yml`, `bootstrap.yml`, `firewall.yml`, `bind.yml`, `nginx.yml`, `install_postgres.yml`, `install_patroni.yml`, `docker.yml`, `docker_compose.yml`, `gitlab.yml`, `harbor.yml`, `host_info.yml`, `server_metrics.yml`, `disable_firewall.yml`, `test_pass.yml`

### Roles (14)
- `roles/bootstrap/`, `firewall/`, `bind/`, `nginx/`, `postgres/`, `patroni/`, `backup/`, `docker/`, `docker_compose/`, `flask_app/`, `gitlab/`, `harbor/`, `host_info/`, `server_metrics/`

### Documentation
- `docs/roles/*/README.md` — 14 documentation files (1 per role)
- `docs/roles/gitlab/GUIDE_RU.md` — Russian guide for GitLab

---

*End of Audit Report*