from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth_router

app = FastAPI(title="Tijzi Auth Backend", version="1.0.0")

# 🔥 CORS PARA ANDROID
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")

# 🔥 ENDPOINT DE PRUEBA
@app.get("/")
def read_root():
    return {"message": "Tijzi Backend is running!", "status": "OK"}

# 🔥 HEALTH CHECK
@app.get("/health")
def health_check():
    return {"status": "healthy"}