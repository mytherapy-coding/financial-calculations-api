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

## Project Structure

```
financial-calculations-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── render.yaml
└── README.md
```
