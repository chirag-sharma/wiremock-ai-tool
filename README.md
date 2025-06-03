# 🤖 AI-Powered WireMock Mapping & Test Case Generator

This tool automates the generation of WireMock mapping files and Excel-based test cases from Swagger/OpenAPI specifications using AI (OpenAI or Gemini). It significantly boosts productivity, improves mock realism, and reduces manual effort in API testing and simulation.

## 🚀 Key Features

-   ✅ **Intelligent WireMock Mapping**
    -   One mapping file per endpoint.
    -   Handles all HTTP methods and status codes.
    -   Supports AI-generated mock responses with realistic JSON.
    -   Adds WireMock response templating (e.g., `{{request.body.someField}}`).

- 📄 **AI-Augmented Test Case Generation**
    -   Excel-based test cases with:
        -   Endpoint
        -   Method
        -   Expected Status
        -   Sample Request & Response
        -   Headers
        -   AI-generated Test Case Description
  
- 🔁 **Multi-Provider AI Integration**
    -   Supports OpenAI and Gemini via a plug-and-play approach.
    -   Handles API key rotation with retry on failure (e.g., 429 errors).
  
- 🛠️ **Configuration Driven**
    -   All behavior controlled via `config.yaml` and `keys.yaml`.
    -   No hardcoding of paths, keys, or parameters.

## 🧱 Project Structure

```
wiremock-ai-tool/
│
├── main.py                      # CLI entry point
├── ai_handler.py                # LLM abstraction (OpenAI/Gemini)
│
├── config/
│   ├── config.yaml              # Tool behavior configuration
│   └── keys.yaml                # API keys for OpenAI/Gemini
│
├── generator/
│   ├── mapping_generator.py     # WireMock mapping generator
│   └── test_case_generator.py   # Excel test case generator
│
├── utils/
│   ├── file_utils.py            # Read/write JSON/Excel/YAML
│   └── retry.py                 # Retry handler with key rotation
│
├── input/                       # User-provided Swagger specs
└── output/
├── mappings/                # Generated WireMock files
└── test_cases/              # Generated Excel test cases
```

## ⚙️ How It Works

1.  Select a Swagger/OpenAPI file interactively.
2.  Tool auto-detects version (2.0 or 3.0) and parses all endpoints.
3.  User selects one or more endpoints.
4.  For each endpoint + method:
    -   AI (or fallback) generates response variants.
    -   WireMock JSON mapping with response templating is generated.
    -   Test cases are generated in Excel (if enabled).
5.  All files are saved in the `output/` directory.

## 📦 Output Example

### 🔹 WireMock Mapping (`output/mappings/POST_pet.json`)

```json
{
  "request": {
    "method": "POST",
    "url": "/pet"
  },
  "response": {
    "status": 201,
    "headers": {
      "Content-Type": "application/json"
    },
    "body": "{ \"id\": \"{{randomValue length=10 type='ALPHANUMERIC'}}\", \"name\": \"{{jsonPath request.body '$.name'}}\" }"
  }
}
```

### 🧠 AI Usage & Safety
1. Uses system prompts to generate only valid JSON mappings.
2. Catches malformed or empty AI responses.
3. Falls back to stub generation if AI is disabled or unavailable.

### 🔧 Configuration (config.yaml)

```
use_ai: true
ai_provider: openai          # or gemini
generate_test_cases: true
output_dir: output/mappings
test_case_dir: output/test_cases
```
### 🔑 API Keys (keys.yaml)
```
openai:
  - sk-xxxx...
  - sk-yyyy...
gemini:
  - gemini-key-1
  - gemini-key-2
```