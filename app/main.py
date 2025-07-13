from fastapi import FastAPI
import httpx

app = FastAPI(title="Tijzi Backend Basic", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "message": "Tijzi Backend is working!", 
        "status": "OK",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/test", "/test-http"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "tijzi-backend",
        "version": "1.0.0"
    }

@app.get("/test")
def test_endpoint():
    return {
        "test": "success", 
        "backend": "running",
        "message": "All systems operational"
    }

@app.post("/ping")
def ping_post(data: dict = None):
    return {
        "message": "POST endpoint working",
        "received_data": data,
        "status": "ok"
    }

# 🔥 NUEVO: Test HTTP requests
@app.get("/test-http")
async def test_http():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/json")
            return {
                "status": "HTTP client working",
                "test_response": response.json(),
                "httpx_version": httpx.__version__
            }
    except Exception as e:
        return {
            "status": "HTTP client error",
            "error": str(e)
        }