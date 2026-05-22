import os.path
from pathlib import Path

from split_settings.tools import include, optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Namespacing our own custom environment settings
ENVVAR_SETTINGS_PREFIX = "PRIMEFLUX_"

DEFAULT_LOCAL_SETTINGS = BASE_DIR / "local/settings.dev.py"

LOCAL_SETTINGS_PATH = Path(
    os.getenv(
        f"{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH",
        DEFAULT_LOCAL_SETTINGS,
    )
)

if not LOCAL_SETTINGS_PATH.is_absolute():
    LOCAL_SETTINGS_PATH = BASE_DIR / LOCAL_SETTINGS_PATH

include(
    "base.py",
    "custom.py",
    optional(str(LOCAL_SETTINGS_PATH)),
    "envvars.py",
)
