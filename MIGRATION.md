# Render Migration Notes

## What changed (render-migration branch)
- Upgraded to **Python 3.11 + Django 5.2 LTS** (from 3.6.9 / 3.0.4).
- Replaced `manage.py runserver` (dev server) with **gunicorn**.
- Added **WhiteNoise** for static files (`CompressedStaticFilesStorage` + middleware).
- Moved secrets (`SECRET_KEY`, `DATABASE_URL`, `CRYPT_KEY`, `DEBUG`, `ALLOWED_HOSTS`) to env vars.
- DB engine switched **MySQL → PostgreSQL** via `dj_database_url` (reads `DATABASE_URL`).
- `mysqlclient` is **kept**: the `execSql` / `sourceTables` views connect to *users' own*
  external MySQL databases — independent of this app's own DB.
- `prod.py` is now safe to commit (no hardcoded secrets); `local.py` stays gitignored.

## Required env vars on Render
| Var | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.9` |
| `DJANGO_SETTINGS_MODULE` | `py_vislib.settings.prod` |
| `SECRET_KEY` | generated (random) |
| `DATABASE_URL` | Neon connection string, e.g. `postgresql://...?sslmode=require` |
| `CRYPT_KEY` | **the existing prod value** (else saved source DB passwords won't decrypt) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `api.pxlab.eu.org,api.v11nlab.com,api.vislib.best,dev.vislib.best,.onrender.com` |

## Deploy
1. Merge `render-migration` → default branch; create a Web Service from this repo on Render
   (it reads `render.yaml`). Or push and let auto-deploy run.
2. `preDeployCommand` runs `collectstatic` + `migrate` automatically before each deploy.

## Load data (one-off, at cutover)
A DB-agnostic fixture was exported with `dumpdata` (excludes contenttypes / permissions /
sessions). The file is NOT committed (it holds user data). Get it from the VPS at
`/home/ubuntu/datadump.json`, then on the Render shell:
```
python manage.py loaddata datadump.json --settings=py_vislib.settings.prod
```

## Cutover
1. Regenerate a fresh fixture right before cutover (data may have changed):
   `python manage.py dumpdata --settings=py_vislib.settings.prod --exclude contenttypes --exclude auth.Permission --exclude sessions -o datadump.json`
2. `loaddata` it on Render.
3. Smoke-test the API on the `*.onrender.com` URL.
4. Point DNS for `api.pxlab.eu.org` / `api.v11nlab.com` / `api.vislib.best` at Render (CNAME).
5. After verified, stop nginx + Django + MySQL on the VPS → the VPS is then free for the
   VPN (Reality can move 8443 → 443).

## Notes / risks
- `SECRET_KEY` is regenerated (new random) — sessions don't carry over (users re-login).
  `django_session` was excluded from the fixture anyway.
- `CRYPT_KEY` was never in git history (old `prod.py` was gitignored) — keep the same value
  to preserve encrypted source passwords.
- Django 3.0 → 5.2 is a big jump; check Render build logs and fix any deprecation errors.
- Render **free** web services sleep after 15 min idle → first request after sleep is slow
  (~cold start). Optional: ping the `*.onrender.com` URL every 10 min (e.g. UptimeRobot) to
  keep it warm.
