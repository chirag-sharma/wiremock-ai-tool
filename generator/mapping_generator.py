import os
import json
import logging

from ai_handler import get_llm_response
from utils.retry import retry_with_key_rotation
from utils.file_utils import write_json_file
from generator.test_case_generator import generate_test_cases

OUTPUT_DIR = "output/mappings"


def build_prompt(yaml_snippet: str) -> str:
    """
    Constructs a prompt to ask LLM to generate WireMock mappings with templated response bodies.
    """
    return f"""Create WireMock mappings for all possible response codes for the following Swagger spec:

{yaml_snippet}

Each mapping should:
- Be a JSON object in an array
- Include a 'request' with method and url
- Include a 'response' with status, body, and headers
- Use response templating syntax (e.g., {{randomValue type='UUID'}}, {{request.query.name}}, etc.)
- Include "transformers": ["response-template"]

Only return pure JSON — no comments or extra text.
"""


def generate_stub_mapping(endpoint: str, method: str) -> list:
    """
    Creates a basic fallback mapping with templated dynamic fields.
    """
    return [{
        "request": {
            "method": method.upper(),
            "url": endpoint
        },
        "response": {
            "status": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "id": "{{randomValue type='UUID'}}",
                "message": f"Hello {{request.query.name}}, your request to {method.upper()} {endpoint} was successful."
            }),
            "transformers": ["response-template"]
        }
    }]


def apply_response_template_to_mappings(mappings: list) -> list:
    """
    Ensures that each mapping has templated body and response-template transformer.
    """
    for mapping in mappings:
        response = mapping.get("response", {})

        # Inject transformers if not present
        if "transformers" not in response:
            response["transformers"] = ["response-template"]

        # Convert body to string if it's a dict and inject sample template
        body = response.get("body")
        if isinstance(body, dict):
            body.setdefault("id", "{{randomValue type='UUID'}}")
            body.setdefault("message", "Hello {{request.query.name}}, your request is processed.")
            response["body"] = json.dumps(body)

        elif isinstance(body, str) and "{{" not in body:
            # Wrap static body with templating (optional fallback)
            response["body"] = f'{{"message": "{body} - {{request.method}} call"}}'

    return mappings


def save_mapping_file(endpoint: str, method: str, mappings: list):
    """
    Saves mappings to disk under output/mappings.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    filename = f"{method.upper()}_{safe_path or 'root'}.json"
    file_path = os.path.join(OUTPUT_DIR, filename)

    try:
        write_json_file(file_path, mappings)
        logging.info(f"💾 WireMock mappings saved: {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to write mapping file: {e}")
        raise


def generate_wiremock_mapping(yaml_snippet: str, config: dict, endpoint: str, method: str):
    """
    Generates WireMock mappings for a given endpoint + method.
    """
    use_ai = config.get("use_ai", False)
    provider = config.get("ai_provider", "openai").lower()
    should_generate_tests = config.get("generate_test_cases", False)

    logging.info(f"🔍 Generating mappings for {method.upper()} {endpoint}")

    if not yaml_snippet.strip():
        logging.warning("⚠️ Empty YAML snippet, skipping...")
        return

    try:
        if use_ai:
            prompt = build_prompt(yaml_snippet)
            logging.info(f"💬 Calling LLM ({provider})...")
            raw_response = get_llm_response(prompt, config)
            mappings = json.loads(raw_response)
        else:
            mappings = generate_stub_mapping(endpoint, method)

        # ✅ Apply templating consistently
        mappings = apply_response_template_to_mappings(mappings)

        # 💾 Save mappings
        save_mapping_file(endpoint, method, mappings)

        # 🧪 Optionally generate test cases
        if should_generate_tests:
            test_case_dir = config.get("test_case_dir", "output/test_cases")
            generate_test_cases(endpoint, method, mappings, config, test_case_dir)

    except Exception as e:
        logging.error(f"❌ Failed to process {method.upper()} {endpoint}: {e}")
