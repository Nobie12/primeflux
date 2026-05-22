def deep_update(base_dict, update_with):
    """
    Recursively updates a dictionary with another dictionary.
    If a key in the update_with dictionary is also a dictionary,
    It will be merged with the corresponding dictionary in base_dict instead of replacing it.

    """
    for key, value in update_with.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict
