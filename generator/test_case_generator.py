import os
import logging
import openpyxl
from openpyxl.styles import Font

from ai_handler import get_llm_response


def generate_test_cases(endpoint, method, mappings, config, output_dir):
    """
    Generates test cases in Excel format based on WireMock mappings.

    Args:
        endpoint (str): API path.
        method (str): HTTP method.
        mappings (list): List of WireMock mappings.
        config (dict): Configuration settings.
        output_dir (str): Directory to save the Excel file.
    """
    logging.info("🧪 Starting test case generation...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Prepare Excel workbook
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Test Cases"

    headers = ["Endpoint", "Method", "Expected Status", "Expected Headers", "Expected Body", "Test Case Description"]
    sheet.append(headers)
    for col in sheet.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
        for cell in col:
            cell.font = Font(bold=True)

    use_ai = config.get("use_ai", False)
    ai_provider = config.get("ai_provider", "openai").lower()

    for mapping in mappings:
        try:
            req = mapping.get("request", {})
            res = mapping.get("response", {})
            status = res.get("status")
            headers = res.get("headers", {})
            body = res.get("body", "")

            if not status:
                logging.warning("⚠️ Skipping mapping with missing status.")
                continue

            # 📄 Build test case description
            if use_ai:
                try:
                    prompt = f"""You're writing test cases for an API mocking tool.

API Endpoint: {endpoint}
HTTP Method: {method.upper()}
Expected Status Code: {status}
Expected Headers: {headers}
Expected Response Body: {body}

Write a clear, concise functional test case description (one line) for validating this scenario."""
                    description = get_llm_response(prompt, config).strip()
                    logging.info(f"🧠 AI-generated description for {method.upper()} {endpoint} [{status}]")
                except Exception as e:
                    logging.warning(f"⚠️ Failed to get AI-generated description. Falling back. Error: {e}")
                    description = f"Verify {method.upper()} {endpoint} returns status {status}."
            else:
                description = f"Verify {method.upper()} {endpoint} returns status {status} with correct headers and body."

            # 📤 Append row
            sheet.append([
                endpoint,
                method.upper(),
                status,
                str(headers),
                str(body),
                description
            ])

        except Exception as e:
            logging.error(f"❌ Failed to process mapping: {e}")
            continue

    # Save workbook
    safe_name = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    excel_file = f"{method.upper()}_{safe_name or 'root'}_test_cases.xlsx"
    output_path = os.path.join(output_dir, excel_file)
    wb.save(output_path)
    logging.info(f"📁 Test cases saved: {output_path}")
