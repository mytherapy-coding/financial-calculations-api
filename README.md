# financial-calculations-api

Stateless JSON API for financial calculations built with FastAPI.

## Quickstart

### Health Check
```bash
curl https://YOUR-RENDER-URL.onrender.com/v1/health
```

**Response:**
```json
{
  "ok": true,
  "service": "finance-api",
  "version": "v1"
}
```

### Echo Endpoint
```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/v1/echo \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, World!",
    "number": 42
  }'
```

**Response:**
```json
{
  "ok": true,
  "echo": {
    "message": "Hello, World!",
    "number": 42
  }
}
```

### Calculate Future Value (Compound Interest)
```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/v1/tvm/future-value \
  -H "Content-Type: application/json" \
  -d '{
    "principal": 10000,
    "annual_rate": 0.07,
    "years": 10,
    "compounds_per_year": 12
  }'
```

**Response:**
```json
{
  "ok": true,
  "future_value": 19671.51
}
```

**Note:** Replace `YOUR-RENDER-URL.onrender.com` with your actual Render deployment URL.

### Interactive API Documentation

Visit `/docs` in your browser for interactive Swagger UI documentation:
- Local: http://127.0.0.1:8000/docs
- Production: https://YOUR-RENDER-URL.onrender.com/docs

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
- **Description:** Check if the API service is running and healthy
- **Response:** `{"ok": true, "service": "finance-api", "version": "v1"}`

### Echo
- **POST** `/v1/echo`
- **Description:** Echo back the request payload. Useful for testing API connectivity.
- **Request body:**
  ```json
  {
    "message": "string",
    "number": 123  // optional
  }
  ```
- **Response:** `{"ok": true, "echo": {...}}`

### Future Value (Compound Interest)
- **POST** `/v1/tvm/future-value`
- **Description:** Calculate the future value of an investment using compound interest.
- **Formula:** FV = P × (1 + r/n)^(n×t)
- **Request body:**
  ```json
  {
    "principal": 10000,
    "annual_rate": 0.07,  // 7% as decimal (not 7)
    "years": 10,
    "compounds_per_year": 12  // monthly
  }
  ```
- **Response:** `{"ok": true, "future_value": 19671.51}`
- **Note:** `annual_rate` must be a decimal (0.07 for 7%, not 7)

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

## Deploy to Render

### Prerequisites
- GitHub repository (this project should be pushed to GitHub)
- Render account (sign up at https://render.com/)

### Deployment Steps

1. **Push to GitHub** (if not already done)
   ```bash
   git push origin main
   ```

2. **Create Render Web Service**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select the repository
   - Configure the service:
     - **Name**: `finance-api` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free tier is available

3. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for deployment to complete (usually 2-3 minutes)

4. **Verify Deployment**
   - Health check: `https://<your-service>.onrender.com/v1/health`
   - API docs: `https://<your-service>.onrender.com/docs`

### Troubleshooting

- **Service crashes**: Check Render logs in the dashboard
- **404 errors**: Verify start command points to `app.main:app`
- **Port errors**: Must use `$PORT` environment variable (don't hardcode port 8000)
- **Build fails**: Check that `requirements.txt` is correct and all dependencies are listed

### Using render.yaml (Optional)

The project includes a `render.yaml` file for automatic configuration. When creating a new service, Render will detect and use this file automatically.

## Web Client

A simple web client is included in the `client/` directory that can call the API from a browser.

### Setup Client

1. **Update API URL** in `client/app.js`:
   ```javascript
   const API_BASE = "https://YOUR-RENDER-URL.onrender.com"; // Replace with your Render URL
   ```

2. **Test locally**:
   - Open `client/index.html` in your browser
   - Click "Check Health" or "Send Echo" buttons
   - Make sure your Render API is deployed and CORS is configured

### Deploy to GitHub Pages

1. **Push client files to GitHub** (already in the repo)

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Select "Deploy from a branch"
   - Branch: `main` (or `gh-pages`)
   - Folder: `/client` (or `/root` if client is at root)
   - Click "Save"

3. **Update CORS in Backend**:
   - The backend already includes CORS middleware
   - Make sure your GitHub Pages URL is in the `allow_origins` list in `app/main.py`
   - Example: `"https://mytherapy-coding.github.io"`

4. **Verify Deployment**:
   - Your client will be available at: `https://<username>.github.io/<repo-name>/client/`
   - Or if using a custom domain: `https://yourdomain.com`

### Client Features

- **Health Check**: Tests the `/v1/health` endpoint
- **Echo**: Sends a POST request to `/v1/echo` with sample data
- **JSON Display**: Shows formatted JSON responses

### CORS Configuration

The backend includes CORS middleware with a **strict allowlist** of frontends that are allowed to call the API.

By default, the following origins are allowed:
- Local development:
  - `http://localhost:8000`
  - `http://127.0.0.1:8000`
  - `http://localhost:3000`
  - `http://127.0.0.1:3000`
- GitHub Pages for this project:
  - `https://mytherapy-coding.github.io`

If you add another frontend (for example, a different GitHub Pages site or a custom domain), update `ALLOWED_ORIGINS` in `app/main.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your GitHub Pages or custom domains here:
    "https://YOURNAME.github.io",
]
```

> Note: `allow_origins` does **not** support wildcards like `"https://*.github.io"` in the way you might expect.  
> If you really want to allow any `username.github.io` (but not other domains), you can use `allow_origin_regex`, for example:
>
> ```python
> app.add_middleware(
>     CORSMiddleware,
>     allow_origin_regex=r"https://[a-zA-Z0-9-]+\.github\.io",
>     allow_methods=["*"],
>     allow_headers=["*"],
> )
> ```
>
> For most cases, a strict `ALLOWED_ORIGINS` list is safer and easier to reason about.

## Project Structure

```
financial-calculations-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── client/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── requirements.txt
├── render.yaml
└── README.md
```
