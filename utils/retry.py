import time
import random
import logging
import yaml

# Load API keys from config/keys.yaml
def load_api_keys(provider):
    with open("config/keys.yaml", "r") as f:
        keys = yaml.safe_load(f)
    return keys.get(provider, [])

# Retry decorator with key rotation
def retry_with_key_rotation(provider, config):
    api_keys = load_api_keys(provider)
    max_attempts = config.get("retry_attempts", 3)
    delay = config.get("retry_delay_seconds", 2)

    if not api_keys:
        raise ValueError(f"No API keys found for provider '{provider}'")

    def decorator(api_function):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                current_key = random.choice(api_keys)
                kwargs["api_key"] = current_key  # Inject the selected key

                try:
                    return api_function(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Attempt {attempt}/{max_attempts} failed with key ending in {current_key[-4:]}. Reason: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise RuntimeError(f"All {max_attempts} retry attempts failed.")
        return wrapper
    return decorator
