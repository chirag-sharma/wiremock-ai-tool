import os
import logging
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def generate_test_cases(endpoint, method, mappings, config, output_dir):
    """
    Generates test cases based on WireMock mappings and writes them to an Excel (.xlsx) file.

    Args:
        endpoint (str): The API path (e.g., "/pet").
        method (str): The HTTP method (e.g., "POST").
        mappings (list): List of WireMock mapping dictionaries.
        config (dict): Loaded configuration dictionary from config.yaml.
        output_dir (str): Directory path where the Excel file will be saved.
    """
    try:
        logging.info("🧪 Starting test case generation...")

        if not isinstance(mappings, list):
            logging.error(f"❌ Expected mappings to be a list, but got {type(mappings).__name__}")
            return

        os.makedirs(output_dir, exist_ok=True)

        # Create a safe filename
        safe_path = endpoint.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        filename = f"TESTCASES_{method.upper()}_{safe_path or 'root'}.xlsx"
        file_path = os.path.join(output_dir, filename)

        # Create Excel workbook and sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "TestCases"

        # Write header row
        headers = [
            "Test Case Name",
            "Method",
            "Endpoint",
            "Expected Status",
            "Expected Body",
            "Expected Headers",
            "Test Case Description"
        ]
        ws.append(headers)

        # Write each test case
        for idx, mapping in enumerate(mappings, 1):
            request = mapping.get("request", {})
            response = mapping.get("response", {})

            status = response.get("status", "")
            body = response.get("body", "")
            headers_dict = response.get("headers", {})

            test_case_name = f"TC_{method.upper()}_{idx}"
            description = f"Test that {method.upper()} {endpoint} returns {status}"

            row = [
                test_case_name,
                method.upper(),
                endpoint,
                status,
                str(body),
                str(headers_dict),
                description
            ]
            ws.append(row)

        # Auto-resize columns
        for col in ws.columns:
            max_length = 0
            column_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            adjusted_width = max_length + 2
            ws.column_dimensions[column_letter].width = adjusted_width

        # Save Excel file
        wb.save(file_path)
        logging.info(f"✅ Test cases written to Excel: {file_path}")

    except Exception as e:
        logging.error(f"❌ Failed to generate Excel test cases for {method.upper()} {endpoint}: {e}")
