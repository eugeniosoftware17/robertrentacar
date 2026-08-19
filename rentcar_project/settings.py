from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-(n(f5@g^w7_$&f!!uu&3dzr^&qpf39vbj36=vq(5kwv@d2z3q=')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())
PANEL_PATH = config('PANEL_PATH', default='dv-rc-ops')

EMPRESA_NOMBRE = config('EMPRESA_NOMBRE', default='Deja Vu Rent Car')
EMPRESA_TELEFONO = config('EMPRESA_TELEFONO', default='')
EMPRESA_DIRECCION = config('EMPRESA_DIRECCION', default='')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'apps.reservas',
    'apps.vehiculos',
    'apps.clientes',
    'apps.core',
    'apps.calendario',
    'apps.cuentas',
    'apps.mantenimiento',
    'apps.pagos',
    'apps.reportes',
    'apps.configuracion',
    'apps.finanzas',
    'apps.sitio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.ModuloPermisoMiddleware',
    'django.contrib.auth.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rentcar_project.urls'

LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'cuentas:login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.panel_usuario',
                'apps.sitio.context_processors.idioma_publico',
            ],
        },
    },
]

WSGI_APPLICATION = 'rentcar_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santo_Domingo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'public'
STATICFILES_DIRS = [BASE_DIR / 'static']

# El servidor de produccion (LiteSpeed + Passenger) no sirve STATIC_ROOT
# directamente, asi que Whitenoise lo hace desde la propia app Django.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
            if not DEBUG
            else 'django.contrib.staticfiles.storage.StaticFilesStorage'
        ),
    },
}

MEDIA_URL = '/media/'
# MEDIA_ROOT vive dentro de STATIC_ROOT (public/) a proposito: en produccion
# public/ ES el document root de Passenger, asi que los archivos subidos quedan
# como archivos reales en disco bajo el docroot y LiteSpeed/Passenger los sirve
# directo, sin symlinks ni contextos especiales (ver deploy/).
MEDIA_ROOT = STATIC_ROOT / 'media'

# En desarrollo, Django sirve /media/ via rentcar_project.urls (solo DEBUG=True).
# En produccion (LiteSpeed + Passenger + WhiteNoise), /static/ lo sirve WhiteNoise;
# /media/ lo sirve LiteSpeed directamente porque MEDIA_ROOT esta dentro del
# docroot (public/media/), igual que cualquier otro archivo estatico (ver deploy/).

# Videos de entrega/devolución (hasta 100 MB por archivo)
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
