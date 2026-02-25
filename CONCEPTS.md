# Part 0 — Concepts

## What is an API?

An API (Application Programming Interface) is a server that listens for HTTP requests and returns responses.

- Our API will accept JSON and return JSON
- It handles HTTP methods (GET, POST, etc.)
- It responds to requests at specific endpoints (URLs)

## REST (RESTful)

REST is a style/architecture for designing APIs:

- You define **endpoints** (URLs) and **methods** (GET, POST, etc.)
- Examples:
  - `GET /v1/health` → returns status
  - `POST /v1/echo` → accepts JSON and returns JSON
- Follows standard HTTP conventions

## Stateless

**Stateless** means:

- The server does **not** "remember" users or sessions between requests
- Every request contains **all input needed** for that calculation
- No database needed for Phase 1
- Each request is independent and self-contained

## What is OpenAPI?

**OpenAPI** is a machine-readable description of your API:

- Documents all endpoints
- Defines JSON schemas (inputs/outputs)
- Includes examples
- Specifies status codes
- Standard format (YAML/JSON) that tools can read

## What is Swagger?

**Swagger UI** is a web page that reads the OpenAPI spec and provides:

- Interactive documentation
- "Try it out" button to test endpoints
- Auto-generated request examples
- Visual API explorer

## FastAPI Integration

In **FastAPI**:
- OpenAPI + Swagger are **generated automatically** from your code
- You write Python code with type hints
- FastAPI creates the OpenAPI spec and Swagger UI automatically
- No manual documentation needed!
