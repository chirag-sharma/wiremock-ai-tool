import os
import json
import logging
import pandas as pd
from ai_handler import get_llm_response

def generate_test_cases(endpoint, method, mappings, config, output_dir):
    """
    Generates test cases in Excel format based on WireMock mappings.

    Args:
        endpoint (str): API path (e.g., /pet)
        method (str): HTTP method (e.g., POST)
        mappings (list): List of WireMock mapping dictionaries
        config (dict): Loaded config.yaml content
        output_dir (str): Directory path where Excel file will be saved
    """
    os.makedirs(output_dir, exist_ok=True)
    test_cases = []
    use_ai = config.get("use_ai", False)

    logging.info("🧪 Starting test case generation...")

    for i, mapping in enumerate(mappings, start=1):
        try:
            request = mapping.get("request", {})
            response = mapping.get("response", {})
            status = response.get("status", "N/A")
            headers = response.get("headers", {})
            body = response.get("body", {})

            # Convert dicts to strings for Excel
            headers_str = json.dumps(headers, indent=2) if isinstance(headers, dict) else str(headers)
            body_str = json.dumps(body, indent=2) if isinstance(body, dict) else str(body)

            # ✨ AI-generated description
            if use_ai:
                try:
                    prompt = f"""
You are a professional QA engineer. Based on the API details below, write a concise and meaningful one-line test case description:

Endpoint: {endpoint}
HTTP Method: {method.upper()}
Expected Status Code: {status}
Expected Headers: {headers}
Expected Response Body: {body}

Rules:
- Be specific (e.g., "Verify successful pet creation")
- Include conditions or goals (e.g., "when valid input is provided")
- Do not include filler like "This test case is..."
- Write as a single sentence.

Only return the test case description.
"""
                    description = get_llm_response(prompt, config).strip()
                    logging.info(f"🧠 AI description created for {method.upper()} {endpoint} [{status}]")
                except Exception as e:
                    logging.warning(f"⚠️ AI description failed, falling back. Error: {e}")
                    description = f"Verify {method.upper()} {endpoint} returns status {status}."
            else:
                description = f"Verify {method.upper()} {endpoint} returns status {status} with correct response."

            test_cases.append({
                "Test Case ID": f"TC_{method.upper()}_{i}",
                "Endpoint": endpoint,
                "Method": method.upper(),
                "Expected Status": status,
                "Expected Headers": headers_str,
                "Expected Body": body_str,
                "Test Case Description": description
            })

        except Exception as e:
            logging.error(f"❌ Failed to process test case #{i} for {method.upper()} {endpoint}: {e}")

    # ✅ Export to Excel
    if test_cases:
        safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        file_name = f"{method.upper()}_{safe_path or 'root'}_test_cases.xlsx"
        output_path = os.path.join(output_dir, file_name)

        try:
            df = pd.DataFrame(test_cases)
            df.to_excel(output_path, index=False)
            logging.info(f"📄 Test cases written to: {output_path}")
        except Exception as e:
            logging.error(f"❌ Failed to write Excel file: {e}")
    else:
        logging.warning(f"⚠️ No test cases generated for {method.upper()} {endpoint}")
