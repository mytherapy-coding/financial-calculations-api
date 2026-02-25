# financial-calculations-api

Stateless JSON API for financial calculations built with FastAPI.

## Setup

### 1. Create virtual environment
```bash
python -m venv .venv
```

### 2. Activate virtual environment
```bash
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Run Locally

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

## API Endpoints

### Health Check
- **GET** `/v1/health`
- Returns: `{"ok": true, "service": "finance-api", "version": "v1"}`

### Echo
- **POST** `/v1/echo`
- Request body:
  ```json
  {
    "message": "string",
    "number": 123  // optional
  }
  ```
- Returns: `{"ok": true, "echo": {...}}`

## Testing

### Interactive API Documentation (Swagger UI)
Open in your browser: http://127.0.0.1:8000/docs

### Health Check
```bash
curl http://127.0.0.1:8000/v1/health
```

### Echo Endpoint
Test via Swagger UI at `/docs` or use curl:
```bash
curl -X POST http://127.0.0.1:8000/v1/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "number": 42}'
```

## Project Structure

```
financial-calculations-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── README.md
```
