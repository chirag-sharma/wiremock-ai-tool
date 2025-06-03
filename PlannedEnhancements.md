
---

## 📈 Planned Enhancements

Below is a curated roadmap of high-impact enhancements for future versions of the tool.

### ✅ Response Templating Enhancements

- Add dynamic content using:
  - `{{jsonPath request.body '$.name'}}`
  - `{{now format='yyyy-MM-dd'}}`
  - `{{randomValue type='UUID'}}`
  - Conditional logic using `{{#if}}` syntax

---

### ✅ AI Prompt & Parsing Improvements

- Include prompt examples for better AI consistency
- Add stricter schema validation for AI-generated responses
- Use Swagger examples as fallback when AI is disabled

---

### ✅ Swagger Spec-Driven Enhancements

- Better support for content-types like `application/xml`, `multipart/form-data`
- Inject path parameters in mock URLs (e.g., `/users/{id}` → `/users/123`)
- Smart matching using regex, partial matchers

---

### ✅ Test Case Generation Enhancements

- AI-enhanced test descriptions:
  - _"Verify that a POST to /pet with valid input returns 200 and creates a pet"_
- Generate edge case tests (400, 401, 500)
- Include input payloads, expected status codes, headers in Excel

---

### ✅ Usability & Interface Upgrades

- Web UI using Streamlit for easy use by QA/Dev teams
- CLI mode for batch processing of specs
- File watch mode: auto-regenerate mappings on file change

---

### ✅ Multi-Provider & Enterprise Support

- Support multiple AI providers (OpenAI, Gemini, Anthropic)
- Smart load balancing across API keys
- Usage tracking and audit logging

---

### ✅ Export & Interoperability

- Export mocks to Postman collections or Karate test scripts
- Delta mock generation (compare Swagger versions)
- Plugin support to customize mappings or test outputs

---

## 💡 Value Proposition

| Role       | Benefit |
|------------|---------|
| QA Engineer | Rapid test case generation from up-to-date API specs |
| Backend Dev| Auto-generated mocks without hardcoding or stubs |
| Test Automation| Excel test cases ready for integration |
| Manager/Lead| Increased productivity and reduced manual effort |
| Enterprise Architect| Configurable, auditable, and AI-extensible framework |

---

## 🛠️ Requirements

- Python 3.8+
- OpenAI / Gemini API key
- Valid OpenAPI 2.0 or 3.x spec in `.yaml` or `.json`

---


