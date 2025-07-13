from fastapi import FastAPI

app = FastAPI(title="Tijzi Backend Basic", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "message": "Tijzi Backend is working!", 
        "status": "OK",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/test"]
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