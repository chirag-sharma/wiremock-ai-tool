import logging
import yaml
import os

from utils.file_utils import select_input_file, read_json_file
from swagger_parser import load_and_parse_swagger, extract_yaml_for_endpoint
from generator.mapping_generator import generate_wiremock_mapping
from generator.test_case_generator import generate_test_cases


def load_config():
    """
    Loads configuration from 'config/config.yaml'.
    """
    try:
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        logging.info("✅ Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"❌ Failed to load config.yaml: {e}")
        raise


def get_user_selected_endpoints(endpoint_list):
    """
    Prompt user to select one or more endpoints from a numbered list.

    Args:
        endpoint_list (list): List of endpoint paths (e.g., /pets, /users/{id})

    Returns:
        list: List of selected endpoint strings
    """
    print("\nAvailable Endpoints:")
    for idx, ep in enumerate(endpoint_list, 1):
        print(f"  {idx}. {ep}")

    choice = input("\nSelect one or more endpoints by number (comma-separated, e.g. 1,3,5): ").strip()
    selected_indices = [s.strip() for s in choice.split(",")]

    selected_endpoints = []
    for index_str in selected_indices:
        try:
            index = int(index_str)
            selected_endpoints.append(endpoint_list[index - 1])
        except (IndexError, ValueError):
            logging.warning(f"⚠️ Invalid selection ignored: {index_str}")

    if not selected_endpoints:
        raise ValueError("No valid endpoints selected.")

    logging.info(f"✅ Selected endpoints: {selected_endpoints}")
    return selected_endpoints


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Step 1: Load configuration
    config = load_config()

    # Step 2: Prompt user to select Swagger/OpenAPI file
    try:
        swagger_path = select_input_file()
        logging.info(f"📄 Swagger file selected: {swagger_path}")
    except Exception as e:
        logging.error(f"❌ Could not select Swagger file: {e}")
        return

    # Step 3: Parse the Swagger file and extract all endpoints
    try:
        parsed_spec, endpoints = load_and_parse_swagger(swagger_path)
        logging.info(f"📘 Parsed {len(endpoints)} endpoint(s) from the Swagger spec.")
    except Exception as e:
        logging.error(f"❌ Failed to parse Swagger file: {e}")
        return

    if not endpoints:
        logging.warning("⚠️ No endpoints found in the Swagger spec.")
        return

    # Step 4: Prompt user to select one or more endpoints from the list
    endpoint_list = list(endpoints.keys())
    try:
        selected_endpoints = get_user_selected_endpoints(endpoint_list)
    except ValueError as e:
        logging.error(f"❌ {e}")
        return

    # Step 5: For each selected endpoint and method, generate mappings and test cases
    for endpoint in selected_endpoints:
        methods = endpoints.get(endpoint, {})
        logging.info(f"\n🔹 Processing endpoint: {endpoint}")

        for method in methods:
            logging.info(f"⚙️ Generating for {method.upper()} {endpoint}")
            try:
                # Extract the specific YAML portion for this method+endpoint
                yaml_snippet = extract_yaml_for_endpoint(swagger_path, endpoint, method)

                # Generate WireMock mappings using AI or fallback stub
                generate_wiremock_mapping(yaml_snippet, config, endpoint, method)

                # Optionally generate test cases from the mappings
                if config.get("generate_test_cases", False):
                    safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                    filename = f"{method.upper()}_{safe_path or 'root'}.json"
                    filepath = os.path.join("output", "mappings", filename)

                    if os.path.exists(filepath):
                        mappings = read_json_file(filepath)
                        if isinstance(mappings, list):
                            generate_test_cases(endpoint, method, mappings)
                        else:
                            logging.warning(f"⚠️ Unexpected mapping format in {filename}")
                    else:
                        logging.warning(f"⚠️ Mapping file not found: {filepath}")
            except Exception as e:
                logging.error(f"❌ Failed to process {method.upper()} {endpoint}: {e}")

    logging.info("✅ All selected endpoints processed.")


if __name__ == "__main__":
    main()
