# TRAIL-PDF - LLM Context Guide

## Project Overview

**TRAIL** (Transcription and Reading Accessibility Improvement Layer) is a Flask-based web application that converts PDF files into accessible HTML documents for visually impaired users, particularly those using screen readers.

### Core Workflow
1. User uploads PDF → 2. PDF pages converted to images → 3. Images sent to GPT-4o Vision → 4. AI generates accessible descriptions → 5. HTML file with navigation downloaded

---

## Architecture Summary

```
run.py                    # Entry point, Flask app initialization with error handling
app/
├── __init__.py           # Flask app factory (create_app), Babel i18n setup, logging
├── Config.py             # Configuration: paths, API keys, env file management
├── controller/           # Route handlers (Blueprints)
│   ├── main_controller.py    # Index, file upload/delete, language switching
│   ├── file_controller.py    # PDF details, conversion triggers
│   └── image_controller.py   # Single image upload/processing endpoint
├── services/             # Business logic
│   ├── ai_service.py         # OpenAI API integration, token tracking
│   ├── pdf_service.py        # PDF-to-image conversion (PyMuPDF/fitz)
│   └── image_service.py      # Image encoding, validation, temp storage
├── utils/
│   ├── helpers.py            # HTML generation, navigation building
│   └── prompts.py            # AI prompt templates (multi-language)
├── templates/            # Jinja2 HTML templates
└── translations/         # Flask-Babel translations (de)
```

---

## Key Files - What They Do

### Entry Points
| File | Purpose |
|------|---------|
| [run.py](run.py) | Application entry, global exception handler |
| [app/__init__.py](app/__init__.py) | `create_app()` factory, Blueprint registration, logging setup |

### Controllers (Routes)
| File | Routes | Purpose |
|------|--------|---------|
| [main_controller.py](app/controller/main_controller.py) | `/`, `/delete/<filename>`, `/set_language/<lang>` | File listing, upload, deletion, language |
| [file_controller.py](app/controller/file_controller.py) | `/files/<filename>`, `/convert_pdf/<filename>`, `/convert_pdf_n_pages/<filename>` | PDF details, full/partial conversion |
| [image_controller.py](app/controller/image_controller.py) | `/image-upload`, `/process-image` | Single image alt-text generation |

### Services (Business Logic)
| File | Key Functions | Purpose |
|------|---------------|---------|
| [ai_service.py](app/services/ai_service.py) | `send_image_to_ai()`, `process_images_with_ai()` | OpenAI API calls, batch processing |
| [pdf_service.py](app/services/pdf_service.py) | `convert_pdf_to_images()` | PyMuPDF-based PDF→PNG conversion |
| [image_service.py](app/services/image_service.py) | `encode_image()`, `is_valid_image()`, `save_image()` | Base64 encoding, validation |

### Utilities
| File | Key Functions | Purpose |
|------|---------------|---------|
| [helpers.py](app/utils/helpers.py) | `save_texts()`, `process_text_for_html()` | HTML document generation with navigation |
| [prompts.py](app/utils/prompts.py) | `PROMPTS` dict | Multi-language prompt templates for GPT |

### Configuration
| File | Key Settings |
|------|--------------|
| [Config.py](app/Config.py) | `OPENAI_API_KEY`, `GPT_MODEL` (gpt-4o), `UPLOAD_PATH`, `TEMP_IMAGE_PATH` |

---

## Technology Stack

- **Framework**: Flask 3.0 with Blueprints
- **AI**: OpenAI GPT-4o Vision API (direct REST calls via `requests`)
- **PDF Processing**: PyMuPDF (fitz) for PDF→image, PyPDF2 for page counting
- **Internationalization**: Flask-Babel (English, German)
- **Image Processing**: Pillow for validation
- **Deployment**: Docker + docker-compose

---

## Data Flow

```
PDF Upload → main_controller.upload_files()
     ↓
PDF Details → file_controller.file_details()
     ↓
Conversion → file_controller.convert_pdf()
     ↓
pdf_service.convert_pdf_to_images() → temp_images/*.png
     ↓
ai_service.process_images_with_ai() → loops through images
     ↓
ai_service.send_image_to_ai() → OpenAI API (base64 encoded)
     ↓
helpers.save_texts() → generates HTML with navigation
     ↓
Response → HTML file download
```

---

## Supported Languages (Prompts)

The `PROMPTS` dict in [prompts.py](app/utils/prompts.py) contains specialized prompts for:
- `english`, `german`, `bilingual`, `turkish`, `french`, `japanese`

Each prompt instructs GPT-4o how to handle: text, tables (→HTML), code (→`<code>`), math formulas (verbal description), and images.

---

## Configuration & Environment

Required environment variables (`.env` file):
```
OPENAI_API_KEY=sk-...
APP_SECRET_KEY=...
```

Key config in [Config.py](app/Config.py):
- `GPT_MODEL = "gpt-4o"` - The vision model used
- `UPLOAD_PATH` - Where uploaded PDFs are stored
- `TEMP_IMAGE_PATH` - Temporary image storage during conversion
- `TOKEN_USAGE_DIR` - CSV logs for API token usage

---

## Common Modification Points

| Task | File(s) to Modify |
|------|-------------------|
| Add new language | [prompts.py](app/utils/prompts.py) - add to `PROMPTS` dict |
| Change AI model | [Config.py](app/Config.py) - `GPT_MODEL` |
| Modify HTML output | [helpers.py](app/utils/helpers.py) - `save_texts()` |
| Add new routes | Create/modify controllers, register in [__init__.py](app/__init__.py) |
| Change PDF rendering | [pdf_service.py](app/services/pdf_service.py) |
| Adjust AI parameters | [ai_service.py](app/services/ai_service.py) - `max_tokens`, `temperature` |

---

## Testing Notes

- No formal test suite exists currently
- Manual testing via Docker: `docker-compose up` → `http://localhost:7777`
- Token usage logged to CSV in `logs/token_usage/`


