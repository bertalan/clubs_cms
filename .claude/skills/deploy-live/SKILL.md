---
name: deploy-live
description: Deploy ClubCMS to the live bare-metal server (clubs.betabi.it). Only when the user explicitly asks for a deploy.
disable-model-invocation: true
---

# Deploy to live (clubs.betabi.it)

Live = bare metal, venv + gunicorn + systemd (`clubcms`, `clubcms-qcluster`), nginx in front. No Docker in production. Python and PostgreSQL major versions match the dev Docker images; the exact server baseline is kept only in the local, untracked `idea/tasks/BACKLOG.md`.

## Before asking for confirmation

1. Working tree clean and `main` pushed (the script refuses otherwise).
2. `bash clubcms/scripts/ci.sh` prints `CI OK` (ruff, system checks incl. `--deploy`, missing migrations, `.po`, tests, `bash -n` on deploy scripts).
3. GitHub Actions `CI` is green on the commit being deployed.
4. If requirements changed: check they install on Python 3.12.

## Confirm, then run

State in plain prose what will happen (backup, pull, pip install, migrate, collectstatic, restart). Wait for an explicit "yes". Then:

```bash
cd clubcms && bash deploy/clubs.betabi.it/deploy.sh
```

## Script rule

The remote part is an unquoted heredoc (`$SSH_CMD bash <<EOF`). Every variable or `$(...)` meant to run on the server must be escaped as `\$`. Unescaped ones expand on the local machine.

## After

- The script health check must print `PASSED (app=…, edge=…)`.
- On failure: `ssh … journalctl -u clubcms --no-pager -n 50`. Do not retry blindly. Report to the user.
