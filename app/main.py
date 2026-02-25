from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Finance Calculations API",
    version="1.0.0",
    description="Stateless JSON API for financial calculations"
)

class EchoRequest(BaseModel):
    message: str
    number: int | None = None

class EchoResponse(BaseModel):
    ok: bool
    echo: EchoRequest

@app.get("/v1/health")
def health():
    return {"ok": True, "service": "finance-api", "version": "v1"}

@app.post("/v1/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    return {"ok": True, "echo": payload}
