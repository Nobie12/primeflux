LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    # Do not disable Django's built-in loggers (like those for database migrations)
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name} (line {lineno}): {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "django.server": {
            "format": "[{asctime}] {message}",
            "style": "{",
        },
    },
    # Filters: Context-based control
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        # Console handler captures everything
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        # Django's dev server specific console logs
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        # Optional: Optional local fallback file that rotates safely at 10MB
        "local_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django_error.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        # The Root Logger: Captures everything your app and dependencies throw
        "": {
            "handlers": ["console", "local_file"],
            "level": "INFO",
        },
        # Dedicated Django HTTP request logger
        "django.request": {
            "handlers": ["console", "local_file"],
            "level": "ERROR",
            "propagate": False,  # Stop propagation to prevent double logging in root
        },
        # Handles runserver output seamlessly
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        # Silence database queries (DEBUG=True can crash performance by logging all SQL)
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
