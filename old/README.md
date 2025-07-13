
# Tijzi Auth Backend (FastAPI)

## Funcionalidad
- Enviar código OTP vía WhatsApp (Cloud API)
- Verificar código OTP
- Retornar token simple

## Comandos de desarrollo
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Despliegue en Railway
1. Crear proyecto nuevo en [https://railway.app](https://railway.app)
2. Subir este código vía GitHub o ZIP
3. Configurar variables de entorno desde `.env`
4. Railway te dará una URL pública para tu API
