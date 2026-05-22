import yaml

def yaml_coerce(value):
    """
    Coerces a string value to its appropriate type based on YAML parsing.
    For example, "true" will be converted to True, "123" to 123, etc.
    """
    try:
        return yaml.safe_load(value)
    except yaml.YAMLError:
        return value