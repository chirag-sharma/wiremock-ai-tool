import os
import json
import logging

from ai_handler import get_llm_response
from utils.retry import retry_with_key_rotation
from utils.file_utils import write_json_file

OUTPUT_DIR = "output/mappings"


def build_prompt(yaml_snippet: str) -> str:
    """
    Constructs the prompt to send to the LLM based on a Swagger endpoint snippet.
    """
    return f"""Create WireMock mappings for all possible response codes for the following Swagger spec:

{yaml_snippet}

Return the result in JSON array format where each object contains:
- 'request' with 'method' and 'url'
- 'response' with 'status', 'body', and 'headers'

Each mapping should reflect realistic example data and demonstrate response variations using status codes and body conditions.

Only return valid JSON. Do not include any extra explanation or comments.
"""


def generate_stub_mapping(endpoint: str, method: str) -> list:
    """
    Returns a basic WireMock mapping for use when AI is disabled.
    """
    logging.info("⚙️ AI disabled — generating fallback stub mapping.")
    return [{
        "request": {
            "method": method.upper(),
            "url": endpoint
        },
        "response": {
            "status": 200,
            "body": f"{{ \"message\": \"Stub response for {method.upper()} {endpoint}\" }}",
            "headers": {
                "Content-Type": "application/json"
            }
        }
    }]


def save_mapping_file(endpoint: str, method: str, mappings: list):
    """
    Saves the WireMock mappings to a JSON file under the output/mappings directory.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Sanitize endpoint for safe file naming
    safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    file_name = f"{method.upper()}_{safe_path or 'root'}.json"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    try:
        write_json_file(file_path, mappings)
        logging.info(f"💾 WireMock mappings saved: {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to save mappings to file: {e}")
        raise


def generate_wiremock_mapping(yaml_snippet: str, config: dict, endpoint: str, method: str):
    """
    Main function to generate WireMock mappings from a Swagger YAML snippet.

    Args:
        yaml_snippet (str): Partial Swagger YAML string representing a specific endpoint + method.
        config (dict): Configuration dictionary loaded from config.yaml.
        endpoint (str): The API path, like /pet.
        method (str): HTTP method like GET, POST, PUT, etc.
    """
    use_ai = config.get("use_ai", False)
    provider = config.get("ai_provider", "openai").lower()

    logging.info(f"🔍 Generating WireMock mapping for: {method.upper()} {endpoint}")

    if not yaml_snippet.strip():
        logging.warning("⚠️ Empty YAML snippet detected. Skipping.")
        return

    # Case: AI disabled, fallback to static stub
    if not use_ai:
        mappings = generate_stub_mapping(endpoint, method)
        save_mapping_file(endpoint, method, mappings)
        return

    # Case: Use AI to generate realistic mappings
    prompt = build_prompt(yaml_snippet)
    try:
        logging.info(f"💬 Invoking LLM provider '{provider}' for {method.upper()} {endpoint}")
        raw_response = get_llm_response(prompt, config)
    except Exception as e:
        logging.error(f"❌ LLM invocation failed: {e}")
        raise

    try:
        mappings = json.loads(raw_response)
        logging.info(f"✅ Successfully parsed {len(mappings)} mappings from LLM response.")
    except json.JSONDecodeError as e:
        logging.error(f"❌ LLM returned invalid JSON: {e}")
        raise

    save_mapping_file(endpoint, method, mappings)
