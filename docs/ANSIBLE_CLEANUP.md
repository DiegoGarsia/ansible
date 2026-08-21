# Ansible Cleanup

**Date:** 2026-08-14  
**Based on:** `docs/ANSIBLE_AUDIT.md`  
**Scope:** Remove secrets, fix inconsistencies, remove dead code, align documentation with code.

---

## Security Fixes

### 🔴 CRITICAL: GitLab Runner Token Removed from Plaintext

**File:** [`inventory/group_vars/gitlab_hosts.yml`](inventory/group_vars/gitlab_hosts.yml)  
**Change:** Replaced hardcoded `glrt-...` token with `{{ vault_gitlab_runner_token | default('') }}`  
**Action:** Token must be rotated. The real token is no longer in the repository.

### 🔴 CRITICAL: Private SSL Key Replaced with Placeholder

**File:** [`roles/nginx/files/nginx-wildcard.key`](roles/nginx/files/nginx-wildcard.key)  
**Change:** Replaced real RSA private key with an example placeholder and generation instructions  
**Action:** Generate a new certificate before using in production.

### 🔴 CRITICAL: Self-Signed Certificate Replaced with Placeholder

**File:** [`roles/nginx/files/nginx-wildcard.crt`](roles/nginx/files/nginx-wildcard.crt)  
**Change:** Replaced real certificate with an example placeholder  
**Action:** Generate a new certificate before using in production.

### 🔴 CRITICAL: Harbor Admin Password Removed from Documentation

**File:** [`docs/roles/harbor/README.md`](docs/roles/harbor/README.md)  
**Change:** Replaced hardcoded `Harbor12345` with `{{ vault_harbor_admin_password }}`  
**Action:** Password must be changed in the running Harbor instance.

### 🔴 HIGH: Debug Tasks Protected with `no_log`

**File:** [`roles/patroni/tasks/configure.yml`](roles/patroni/tasks/configure.yml)  
**Change:** Added `no_log: true` to debug task that prints passwords

**File:** [`playbooks/test_pass.yml`](playbooks/test_pass.yml)  
**Change:** Added `no_log: true` to both debug tasks

### 🔴 HIGH: `.gitignore` Updated

**File:** [`.gitignore`](.gitignore)  
**Change:** Added `*.crt`, `*.key`, and `.vault_pass` patterns to prevent future secret leaks

### 🔴 HIGH: `harbor_admin_password` Added to Defaults

**File:** [`roles/harbor/defaults/main.yml`](roles/harbor/defaults/main.yml)  
**Change:** Added `harbor_admin_password: "{{ vault_harbor_admin_password }}"` with reference to vault

---

## Role-by-Role Changes

### bootstrap

| File | Change |
|------|--------|
| — | No changes needed. Role is clean. |

### firewall

| File | Change |
|------|--------|
| [`docs/roles/firewall/README.md`](docs/roles/firewall/README.md) | Fixed variable examples to match actual `group_vars/managed.yml`. Removed references to non-existent `group_vars/all.yml`, `local_networks`, `jump_host_sources`. Fixed `firewall_default_forward_policy` from `DROP` to `ACCEPT`. |

### bind

| File | Change |
|------|--------|
| [`docs/roles/bind/README.md`](docs/roles/bind/README.md) | Fixed variable location from `group_vars/all.yml` to `roles/bind/vars/main.yml`. Removed non-existent `dns_allowed_networks` variable. Fixed `dnsutils` → `bind9-dnsutils` in package list. |

### nginx

| File | Change |
|------|--------|
| [`roles/nginx/files/nginx-wildcard.key`](roles/nginx/files/nginx-wildcard.key) | Replaced real private key with placeholder |
| [`roles/nginx/files/nginx-wildcard.crt`](roles/nginx/files/nginx-wildcard.crt) | Replaced real certificate with placeholder |
| [`docs/roles/nginx/README.md`](docs/roles/nginx/README.md) | Fixed claim about DNS names — Nginx actually uses IPs from `hostvars` |

### postgres

| File | Change |
|------|--------|
| [`docs/roles/postgres/README.md`](docs/roles/postgres/README.md) | Fixed incorrect claim about import idempotency. Added note that import runs every time. |

### patroni

| File | Change |
|------|--------|
| [`roles/patroni/tasks/configure.yml`](roles/patroni/tasks/configure.yml) | Added `no_log: true` to debug task |
| [`docs/roles/patroni/README.md`](docs/roles/patroni/README.md) | Fixed title typo: "partoni" → "patroni" |

### backup

| File | Change |
|------|--------|
| [`roles/backup/tasks/cron.yml`](roles/backup/tasks/cron.yml) | **Deleted** — dead code, never imported |
| [`docs/roles/backup/README.md`](docs/roles/backup/README.md) | Fixed variable name from `backup_schedule` to `backup_hour`/`backup_minute`. Fixed markdown formatting. |

### docker

| File | Change |
|------|--------|
| [`docs/roles/docker/README.md`](docs/roles/docker/README.md) | Updated idempotency claim to note `recreate: true` behavior |

### docker_compose

| File | Change |
|------|--------|
| [`docs/roles/docker_compose/README.md`](docs/roles/docker_compose/README.md) | Updated idempotency claim to note `force: true` and `build: always` behavior |

### flask_app

| File | Change |
|------|--------|
| — | No changes needed. Role is clean. |

### gitlab

| File | Change |
|------|--------|
| [`inventory/group_vars/gitlab_hosts.yml`](inventory/group_vars/gitlab_hosts.yml) | Replaced hardcoded token with vault reference |
| [`docs/roles/gitlab/README.md`](docs/roles/gitlab/README.md) | Fixed vault path from `group_vars/gitlab/vault.yml` to `inventory/group_vars/vault.yml` |

### harbor

| File | Change |
|------|--------|
| [`roles/harbor/defaults/main.yml`](roles/harbor/defaults/main.yml) | Added `harbor_admin_password` with vault reference |
| [`docs/roles/harbor/README.md`](docs/roles/harbor/README.md) | Removed hardcoded password, replaced with vault reference |

### host_info

| File | Change |
|------|--------|
| — | No changes needed. Role is clean. |

### server_metrics

| File | Change |
|------|--------|
| — | No changes needed. Role is clean. |

---

## Removed Duplication

| What | Where | Action |
|------|-------|--------|
| `cron.yml` task file | `roles/backup/tasks/cron.yml` | Deleted — never imported, systemd timer is the active implementation |
| `etcd.conf.yml.j2` template | `roles/patroni/templates/etcd.conf.yml.j2` | Deleted — never used, etcd is configured via command-line args in service template |

---

## Fixed Inconsistencies

| Inconsistency | Fix |
|---------------|-----|
| `lxc_proxy` group pointed to nginx IP (192.168.0.101) instead of docker (192.168.0.102) | Fixed IP in `inventory/hosts.ini` |
| `kvm_proxy` group pointed to nginx IP (192.168.0.101) instead of centos (192.168.0.150) | Fixed IP in `inventory/hosts.ini` |
| Firewall docs referenced `group_vars/all.yml` which doesn't exist | Changed to reference `group_vars/managed.yml` |
| Firewall docs referenced `local_networks` and `jump_host_sources` which don't exist | Replaced with actual hardcoded values from `managed.yml` |
| Firewall docs said `firewall_default_forward_policy: DROP` but code has `ACCEPT` | Fixed docs to match code |
| Bind docs referenced `dns_allowed_networks` which doesn't exist | Removed from docs |
| Bind docs said variables are in `group_vars/all.yml` | Changed to `roles/bind/vars/main.yml` |
| Backup docs referenced `backup_schedule` but code uses `backup_hour`/`backup_minute` | Fixed docs |
| Nginx docs said DNS names are used but code uses IPs | Fixed docs |
| Postgres docs claimed import is idempotent | Fixed docs with accurate note |
| Patroni docs title had typo "partoni" | Fixed to "patroni" |
| GitLab docs referenced wrong vault path | Fixed to `inventory/group_vars/vault.yml` |
| Docker docs claimed full idempotency | Updated with note about `recreate: true` |
| Docker Compose docs claimed full idempotency | Updated with notes about `force: true` and `build: always` |

---

## Documentation Fixes

| Doc File | Changes |
|----------|---------|
| `docs/roles/firewall/README.md` | Fixed variable examples, removed non-existent references |
| `docs/roles/bind/README.md` | Fixed variable location, removed non-existent variable |
| `docs/roles/nginx/README.md` | Fixed DNS vs IP claim |
| `docs/roles/postgres/README.md` | Fixed idempotency claim |
| `docs/roles/patroni/README.md` | Fixed title typo |
| `docs/roles/backup/README.md` | Fixed variable names, fixed markdown |
| `docs/roles/docker/README.md` | Updated idempotency note |
| `docs/roles/docker_compose/README.md` | Updated idempotency note |
| `docs/roles/gitlab/README.md` | Fixed vault path |
| `docs/roles/harbor/README.md` | Removed hardcoded password |

---

## Removed Dead Code

| File | Reason |
|------|--------|
| `roles/backup/tasks/cron.yml` | Never imported in `main.yml`. Systemd timer is the active implementation. |
| `roles/patroni/templates/etcd.conf.yml.j2` | Never used. etcd is configured via command-line arguments in `etcd.service.j2`. |

---

## Remaining Idempotency Issues

These issues are **not fixed** in this cleanup. They will be addressed in a separate idempotency-focused phase.

| Role | Issue | Severity |
|------|-------|----------|
| `bootstrap` | `apt upgrade: dist` always reports changed | Low |
| `postgres` | SQL import runs every time despite table check | Medium |
| `docker` | `recreate: true` forces container restart every run | Medium |
| `docker_compose` | `get_url` with `force: true` downloads every run | Low |
| `docker_compose` | `build: always` rebuilds images every run | Medium |
| `harbor` | `get_url` downloads installer every run (no `force: false`) | Low |
| `harbor` | `lineinfile`/`replace` tasks modify config every run | Medium |
| `harbor` | `command` task runs `prepare` every run without `creates` | Medium |
| `harbor` | Docker restart on every run (not using handler) | High |
| `bind` | Zone serial number changes daily via `strftime` | Low |
| `gitlab` | `gitlab-ctl restart` handler always reports changed | Low |

---

## Remaining Technical Debt

| Item | Priority | Notes |
|------|----------|-------|
| No `meta/dependencies` declared in any role | P2 | All dependencies are implicit |
| Role duplication: `docker` vs `docker_compose` vs `flask_app` | P2 | Three ways to deploy Flask apps |
| `host_key_checking = False` in `ansible.cfg` | P1 | Disabled for lab, but should be enabled for production |
| etcd without authentication | P1 | Listens on `0.0.0.0:2379` with no TLS |
| Patroni REST API without authentication | P1 | Listens on `0.0.0.0:8008` with no auth |
| PostgreSQL `pg_hba` allows all from `0.0.0.0/0` | P1 | Should be restricted to specific hosts |
| Flask runs as root | P2 | Should run as unprivileged user |
| Docker daemon.json conflicts between gitlab and harbor roles | P2 | Both overwrite this file |
| No `host_vars/` directory | P3 | For per-host configuration |
| No `group_vars/all.yml` | P3 | For truly shared variables |

---

## Recommended Next Steps

1. **Rotate the GitLab Runner token** — The exposed token `glrt-rN4RSzN-...` is compromised. Generate a new token in GitLab UI and update it in `inventory/group_vars/vault.yml`.

2. **Generate new SSL certificate** — Run the openssl command from `roles/nginx/files/openssl.cnf` to create a new wildcard certificate and key, then update the placeholder files.

3. **Change Harbor admin password** — The default password was exposed in documentation. Change it in the running Harbor instance and store the new password in vault.

4. **Address idempotency issues** — Run a dedicated idempotency pass focusing on the `harbor` role (worst offender) and the `docker`/`docker_compose` roles.

5. **Add `meta/dependencies`** — Declare explicit role dependencies to make execution order clear.

6. **Add authentication to etcd and Patroni** — For any production or persistent lab use, add TLS and authentication.

---

## Validation

| Check | Result |
|-------|--------|
| `ansible-playbook --syntax-check` on all 15 playbooks | ✅ PASS |
| No real secrets in repository | ✅ Verified |
| No private keys in repository | ✅ Verified |
| No hardcoded credentials in documentation | ✅ Verified |
| Inventory proxy group IPs corrected | ✅ Verified |
| Dead code removed | ✅ Verified |
| Documentation matches actual code | ✅ Verified |

---

*End of Cleanup Report*