def verify_dict_keys(dict_list):
    """
    Verifies that all dictionaries in the list have the same keys.

    Args:
        dict_list (list): A list of dictionaries to verify.

    Returns:
        bool: True if all dictionaries have the same keys, False otherwise.
        set: The set of keys that all dictionaries should have.
        list: A list of dictionaries that are missing or have extra keys.
    """
    if not dict_list:
        print("The list is empty.")
        return False, set(), []

    # Get the keys of the first dictionary as the reference
    reference_keys = set(dict_list[0].keys())
    inconsistent_dicts = []

    # Check each dictionary against the reference keys
    for i, d in enumerate(dict_list):
        current_keys = set(d.keys())
        if current_keys != reference_keys:
            inconsistent_dicts.append({
                "index": i,
                "keys_found": current_keys,
                "missing_keys": reference_keys - current_keys,
                "extra_keys": current_keys - reference_keys
            })

    # If there are inconsistencies, print details
    if inconsistent_dicts:
        print("Inconsistent dictionaries found:")
        for issue in inconsistent_dicts:
            print(f"Dictionary at index {issue['index']}:")
            print(f"  Missing keys: {issue['missing_keys']}")
            print(f"  Extra keys: {issue['extra_keys']}")
        return False, reference_keys, inconsistent_dicts

    print("All dictionaries have the same keys.")
    return True, reference_keys, []

# Example usage
dict_list = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "Los Angeles"},
    {"name": "Charlie", "age": 35, "state": "California"}  # Inconsistent keys
]

result, keys, issues = verify_dict_keys(dict_list)
print(f"All dictionaries have the same keys: {result}")
print(f"Expected keys: {keys}")