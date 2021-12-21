"""
Django settings for sober_site project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


# that file must be changed for non-local deployment and kept secret
from .site_specific_settings import (
    SECRET_KEY,
    DEBUG,
    ALLOWED_HOSTS,
    DATABASES,
    MACHINE_NAME,
    FEEDBACK_RECEIVER,
    FEEDBACK_SENDER,
    EMAIL_BACKEND,
    EMAIL_USE_TLS,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    BACKUP_PATH,
    SIMPLE_PAGE_CONTENT_CUSTOM_PATH,
)

# Application definition

INSTALLED_APPS = [
    "sober.apps.SoberAppConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_nose",
    "captcha",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "sober_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sober_site.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

# default; will be overridden by user-specific settings
LANGUAGE_CODE = "en-us"

# django will look within each of these paths for the <locale_code>/LC_MESSAGES directories
# containing the actual translation files.

import sober.utils

LOCALE_PATHS = [sober.utils.get_path("locale")]


TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_L10N = True

USE_TZ = True


CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.math_challenge"
CAPTCHA_NOISE_FUNCTIONS = ("captcha.helpers.noise_dots",)
# in minutes
# TODO: instead of such a high value the timeout handling should be improved
CAPTCHA_TIMEOUT = 90
CAPTCHA_FONT_SIZE = 30
CAPTCHA_LETTER_ROTATION = (-10, 10)

if DEBUG:
    CAPTCHA_TEST_MODE = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


# this is the target of manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static_files")

# the url which will be included in the templates like:
# <link rel="stylesheet" href="{{ STATIC_URL }}css/base.css" type="text/css" />
STATIC_URL = "/static/"

# such requests will be mapped to the directory above by the (appropriatly configured webserver)