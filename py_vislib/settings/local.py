from .base import *
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vislib',
        'USER': 'root',
        'PASSWORD': '123456xxf',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

CRYPT_KEY = 'keyskeyskeyskeys'
