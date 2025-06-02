import os
import logging
from openpyxl import Workbook

OUTPUT_DIR = "output/test_cases"

def generate_test_cases(endpoint: str, method: str, responses: list):
    """
    Generates Excel test cases for an endpoint and saves them under output/test_cases.

    Args:
        endpoint (str): The API path (e.g., "/pet/{id}").
        method (str): HTTP method (e.g., "get", "post").
        responses (list): A list of WireMock-style response dicts (LLM or stub generated).
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    file_name = f"{method.upper()}_{safe_path or 'root'}.xlsx"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    # Header
    ws.append(["Test Case ID", "Endpoint", "Method", "Expected Status", "Expected Body Preview", "Headers"])

    for idx, resp in enumerate(responses, 1):
        status = resp.get("response", {}).get("status", "")
        body = resp.get("response", {}).get("body", "")
        headers = resp.get("response", {}).get("headers", {})

        ws.append([
            f"TC_{idx:03}",
            endpoint,
            method.upper(),
            status,
            str(body)[:100].replace("\n", " "),  # Trim + flatten for Excel preview
            ", ".join(f"{k}: {v}" for k, v in headers.items())
        ])

    try:
        wb.save(file_path)
        logging.info(f"📄 Test cases saved: {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to save Excel file: {e}")
        raise
