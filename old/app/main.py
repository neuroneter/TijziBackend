from fastapi import FastAPI

app = FastAPI(title="Tijzi Backend Basic", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Tijzi Backend is working!", "status": "OK"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "tijzi-backend"}

@app.get("/test")
def test_endpoint():
    return {"test": "success", "backend": "running"}