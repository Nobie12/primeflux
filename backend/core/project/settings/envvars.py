from core.core_functions.utils.collections import deep_update
from core.core_functions.utils.settings import get_settings_from_environment

"""
This takes env variables with matching prefix, strips the prefix, and adds it to global variables.

For example:
export PRIMEFLUX_IN_DOCKER=true (environment variable)

could then be referenced as:
IN_DOCKER (where the value would be true)

"""

# globals() is a dictionary of the gloabl variables
deep_update(globals(), get_settings_from_environment(ENVVAR_SETTINGS_PREFIX))
