from.base import *

DEBUG = config('DEBUG')



DATABASES = {
    "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
 }
}
INTERNAL_IPS = [
    "127.0.0.1",
]