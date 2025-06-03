import logging
import os
import pandas as pd

from ai_handler import get_llm_response  # ai_handler is in root, not in utils

# ===============================
# 🧪 Test Case Generation Module
# ===============================
def generate_test_cases(endpoint, method, responses, config, output_dir):
    try:
        logging.info("🧪 Starting test case generation...")

        test_cases = []
        use_ai = config.get("use_ai", False)

        for idx, (status_code, response_info) in enumerate(responses.items(), start=1):
            # Basic values
            test_case_id = f"TC_{str(idx).zfill(3)}"
            expected_status = int(status_code)
            expected_body = response_info.get("body", "") or "{}"

            # Determine content-type header (if available)
            headers = response_info.get("headers", {})
            headers_str = ", ".join([f"{k}: {v}" for k, v in headers.items()])

            # ✨ Description logic
            if use_ai:
                try:
                    prompt = (
                        f"Write a concise test case description for an API request to {method.upper()} {endpoint} "
                        f"that expects HTTP {expected_status}."
                    )
                    description = get_llm_response(prompt, config).strip()
                except Exception as e:
                    logging.warning(f"⚠️ AI description fallback: {e}")
                    description = f"Validate {method.upper()} {endpoint} returns {expected_status}"
            else:
                # Fallback if AI is disabled
                description = f"Validate {method.upper()} {endpoint} returns {expected_status}"

            # Construct test case row
            test_cases.append({
                "Test Case ID": test_case_id,
                "Endpoint": endpoint,
                "Method": method.upper(),
                "Expected Status": expected_status,
                "Expected Body Preview": expected_body,
                "Headers": headers_str,
                "Test Case Description": description
            })

        # Write to Excel
        df = pd.DataFrame(test_cases)
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{method.upper()}_{endpoint.strip('/').replace('/', '_')}_test_cases.xlsx")
        df.to_excel(file_path, index=False)

        logging.info(f"✅ Test cases saved: {file_path}")

    except Exception as e:
        logging.error(f"❌ Failed to process {method.upper()} {endpoint}: {e}")
