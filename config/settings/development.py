from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cozyshop'),
        'USER': os.environ.get('DB_USER', 'cozyshop'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'cozyshop'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
