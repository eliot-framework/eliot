# Django settings for project.

import os


SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Everton', 'evertonagilar@gmail.com'),
)

#try:
#    import pymysql
#    pymysql.install_as_MySQLdb()
#except ImportError:
#    pass

# config para Mysql
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql', 
#        'NAME':  'acesso',                      
#        'USER': 'root',
#        'PASSWORD': '960101',
#        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#        'PORT': '3306',                      # Set to empty string for default.
#    }
#}

# config para PostgreSQL
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
#        'NAME':  'desenv',
#        'OPTIONS': {
#                'options': '-c search_path=acesso,public'
#         },
#        'USER': 'evertonagilar',
#        'PASSWORD': '960101',
#        'HOST': '10.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#        'PORT': '5432',                      # Set to empty string for default.
#    }
#}

# config para sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME':  os.path.normpath(os.path.dirname(__file__)) + os.sep + 'db' + os.sep + 'database.db',                      
    }
}


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"

#STATIC_ROOT = os.path.join(SETTINGS_PATH, "static/")

STATIC_URL = "/eliot/static/"


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SETTINGS_PATH, "static/"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '41gl2vndt!^9pju5tkqnqc^il+f!8e76dsl@v8f#%)bcq$idir'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    #'debug_panel.middleware.DebugPanelMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'fpc.middleware.JsonAsHTML',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fpc.middleware.MonitoraSQLMiddleware',
    
)


ROOT_URLCONF = 'eliot.urls'


# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'eliot.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fpc',
    'adm',
    'estoque',  
    'sae',
    'eliot.apps.EliotConfig',
     
    #'debug_panel',
    
)

INTERNAL_IPS = ('127.0.0.1')


FPC_REGISTER_MODULES = (
    'adm', 'estoque', 'sae'
)

SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'
#SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


TEST_RUNNER = 'django.test.runner.DiscoverRunner'


# Configurações específicas do sistema

MANTEM_FORM_CACHE = False

HTML5_CACHE = False
HTML5_HASH_CACHE = "12"

USE_GZIP = False
USE_CLOSURE_COMPILE = False
USE_CSSMINIFIER = False

IP_ERLANGMS = "localhost" 
PORT_ERLANGMS = 2301
