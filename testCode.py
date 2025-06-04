import logging
from ai_handler import get_llm_response

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    """
    Entry point for testing integration with the organization's LLM provider.
    This script verifies that the org_llm configuration works correctly and
    that a response can be retrieved successfully.
    """

    # Sample test configuration for the org_llm provider
    test_config = {
        "ai_provider": "org_llm",
        "org_llm": {
            "api_key": "your-org-api-key",  # Replace with actual key or use an environment variable
            "api_endpoint": "https://llm.myorg.internal/v1/chat",  # Replace with actual endpoint
            "model": "myorg-gpt-4",
            "temperature": 0.7
        }
    }

    # Prompt to test LLM output
    test_prompt = (
        "Briefly explain what WireMock is and how it is typically used "
        "in software development and API testing."
    )

    try:
        logging.info("Starting test for organization-specific LLM integration.")
        response = get_llm_response(test_prompt, test_config)
        logging.info("LLM response received successfully.")
        print("LLM Output:\n")
        print(response)

    except Exception as e:
        logging.error(f"Test failed during LLM invocation: {e}")


if __name__ == "__main__":
    main()
