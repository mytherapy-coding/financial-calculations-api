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

The backend includes CORS middleware to allow requests from:
- Localhost (for development)
- GitHub Pages domains (`*.github.io`)
- Your specific GitHub Pages URL

If you need to add more origins, update `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://YOURNAME.github.io",  # Add your GitHub Pages URL
        "https://*.github.io",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

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
