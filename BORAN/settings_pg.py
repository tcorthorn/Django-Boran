from .settings import *  # hereda TODO lo demás (INSTALLED_APPS, MIDDLEWARE, etc.)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "BoranPG",
        "USER": "postgres",
        "PASSWORD": "123321",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
