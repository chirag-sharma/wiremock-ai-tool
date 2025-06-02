import logging
from configparser import ConfigParser

from utils.file_utils import select_input_file
from swagger_parser import load_and_parse_swagger
from generator.mapping_generator import generate_wiremock_mapping
from generator.test_case_generator import generate_test_cases
import yaml
import os

# ----------------------
# Logging Configuration
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ----------------------
# Load YAML Configuration
# ----------------------
def load_config():
    config_path = os.path.join("config", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# ----------------------
# Main Entry Point
# ----------------------
def main():
    config = load_config()

    # Step 1: File Selection
    input_file_path = select_input_file()

    # Step 2: Parse Swagger/OpenAPI
    spec, endpoints = load_and_parse_swagger(input_file_path)
    if not endpoints:
        logging.warning("No endpoints found in the Swagger file.")
        return

    # Step 3: Process each endpoint
    for endpoint, methods in endpoints.items():
        if not methods:
            logging.warning(f"⚠️ No methods found for path: {endpoint}")
            continue
        logging.info(f"🔍 Processing endpoint: {endpoint}")

        for method, yaml_snippet in methods.items():
            try:
                generate_wiremock_mapping(yaml_snippet, config, endpoint, method)

                if config.get("generate_test_cases", False):
                    # Reuse the generated mappings for test case generation
                    import json
                    from utils.file_utils import read_json_file

                    safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                    filename = f"{method.upper()}_{safe_path or 'root'}.json"
                    filepath = os.path.join("output", "mappings", filename)

                    if os.path.exists(filepath):
                        mappings = read_json_file(filepath)
                        generate_test_cases(endpoint, method, mappings)
            except Exception as e:
                logging.error(f"❌ Error processing {method.upper()} {endpoint}: {e}")

    logging.info("✅ Done.")

if __name__ == "__main__":
    main()
