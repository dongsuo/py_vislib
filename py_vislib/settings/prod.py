from .base import *
import os
import dj_database_url

# Production overrides.
# All secrets (SECRET_KEY, DATABASE_URL, CRYPT_KEY, DEBUG, ALLOWED_HOSTS) come
# from environment variables set on Render. This file contains NO hardcoded
# secrets and is safe to commit (unlike the old prod.py which was gitignored).

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Cookies: the frontend is on a different origin, so allow cross-site
# session/CSRF cookies over HTTPS.
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None

# CORS: the frontend is on a different origin. The old VPS deploy had nginx
# reflect $http_origin with credentials; on Render there's no nginx in front,
# so django-cors-headers does the equivalent here. With both flags set it
# reflects the request Origin (NOT "*", which the CORS spec forbids together
# with credentials) — same behaviour the old nginx block produced.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Database: PostgreSQL via DATABASE_URL.
# On Render, set DATABASE_URL to the Neon connection string.
# Locally (no DATABASE_URL), fall back to sqlite so `manage.py check/migrate`
# works without a database configured.
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=60, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# CRYPT_KEY: AES key for the encrypted SourceDataBase.password field
# (users' external DB passwords stored in this app's own DB).
# IMPORTANT: must equal the value used when the data was created, otherwise
# existing SourceDataBase.password values become undecryptable. Set via env.
CRYPT_KEY = os.environ.get('CRYPT_KEY', '')
