import logging
import requests
import json
from openai import OpenAI

from utils.retry import retry_with_key_rotation

# ========================
# Organization LLM Handler
# ========================
def call_org_llm(prompt: str, config: dict) -> str:
    """
    Calls the organization's internal LLM API and returns the response.

    Args:
        prompt (str): Input prompt to send to the model.
        config (dict): Contains 'org_llm' keys: api_key, api_endpoint, model, temperature.

    Returns:
        str: Textual response from the model.
    """
    org_llm_config = config.get("org_llm", {})

    headers = {
        "Authorization": f"Bearer {org_llm_config.get('api_key')}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "model": org_llm_config.get("model", "myorg-gpt-4"),
        "temperature": org_llm_config.get("temperature", 0.7)
    }

    try:
        logging.info("Calling organization's internal LLM API.")
        response = requests.post(org_llm_config.get("api_endpoint"), headers=headers, json=payload)
        response.raise_for_status()

        response_json = response.json()
        result = response_json.get("text") or response_json.get("response") or json.dumps(response_json)

        logging.info("Received response from organization's internal LLM.")
        return result
    except Exception as e:
        logging.exception("Organization LLM API call failed.")
        raise


# ========================
# OpenAI LLM Handler
# ========================
def call_openai(prompt, api_key, model="gpt-3.5-turbo"):
    """
    Calls OpenAI ChatCompletion API using the new SDK.

    Args:
        prompt (str): The user prompt.
        api_key (str): OpenAI API key.
        model (str): Model to use (default: gpt-3.5-turbo).

    Returns:
        str: The generated response.
    """
    try:
        logging.info(f"Calling OpenAI ChatCompletion | Model: {model}")
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("OpenAI API call failed.")
        raise RuntimeError(f"OpenAI call failed: {e}")


# ========================
# Gemini LLM Handler
# ========================
def call_gemini(prompt, api_key):
    """
    Calls Gemini API to generate content.

    Args:
        prompt (str): The input prompt.
        api_key (str): Gemini API key.

    Returns:
        str: Generated response text.
    """
    try:
        logging.info("Calling Gemini API | Model: gemini-pro")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(
            url, headers=headers, json=payload, params={"key": api_key}
        )
        response.raise_for_status()

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logging.exception("Gemini API call failed.")
        raise RuntimeError(f"Gemini call failed: {e}")


# ========================
# Unified LLM Dispatcher
# ========================
def get_llm_response(prompt, config):
    """
    Unified handler that dispatches the prompt to the selected AI provider.

    Args:
        prompt (str): The prompt to send.
        config (dict): Contains 'use_ai', 'ai_provider', and provider-specific keys.

    Returns:
        str: AI-generated response text.
    """
    if not config.get("use_ai", False):
        logging.info("AI usage is disabled. Skipping LLM call.")
        return ""

    provider = config.get("ai_provider", "openai").lower()
    logging.info(f"Using AI provider: {provider}")

    if provider == "openai":
        model = config.get("openai", {}).get("model", "gpt-3.5-turbo")

        @retry_with_key_rotation("openai", config)
        def call(prompt, api_key=None):
            return call_openai(prompt, api_key=api_key, model=model)

    elif provider == "gemini":
        @retry_with_key_rotation("gemini", config)
        def call(prompt, api_key=None):
            return call_gemini(prompt, api_key=api_key)

    elif provider == "org_llm":
        @retry_with_key_rotation("org_llm", config)
        def call(prompt, api_key=None):
            # 'api_key' is passed for consistency, although it's read from config inside
            return call_org_llm(prompt, config)

    else:
        logging.error(f"Unsupported AI provider: {provider}")
        raise ValueError(f"Unsupported AI provider: {provider}")

    return call(prompt)
