import logging
import openai
import requests

from utils.retry import retry_with_key_rotation

# ===========================
# OpenAI Handler (with retry)
# ===========================
#@retry_with_key_rotation(provider="openai", config=None)
def call_openai(prompt, api_key):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"OpenAI call failed: {e}")


# ============================
# Gemini Handler (with retry)
# ============================
#@retry_with_key_rotation(provider="gemini", config=None)
def call_gemini(prompt, api_key):
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(
            url, headers=headers, json=payload, params={"key": api_key}
        )
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.status_code} - {response.text}")

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Gemini call failed: {e}")


# ===========================================
# Unified Entry Point: Use in your generators
# ===========================================
def get_llm_response(prompt, config):
    if not config.get("use_ai", False):
        logging.info("⚠️  AI usage is disabled. Skipping LLM call.")
        return ""

    provider = config.get("ai_provider", "openai")
    logging.info(f"🔍 Using AI provider: {provider}")

    # Dynamically re-bind the retry decorator with active config
    if provider == "openai":
        call_fn = retry_with_key_rotation("openai", config)(call_openai.__wrapped__)
    elif provider == "gemini":
        call_fn = retry_with_key_rotation("gemini", config)(call_gemini.__wrapped__)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

    return call_fn(prompt)
