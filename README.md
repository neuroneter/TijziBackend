# Tijzi Backend Básico
Servicio usado para desplegar Render, ruta de despliegue https://tijzibackend.onrender.com/

# 🚀 Tijzi - Sistema de Autenticación OTP vía WhatsApp

## 📋 **Estado del Proyecto (Actualizado: Agosto 2025)**

✅ **Backend funcionando al 100%**  
✅ **Integración WhatsApp Business API completa**  
✅ **Envío y verificación de códigos OTP operativos**  
✅ **Arquitectura Kotlin Multiplatform preparada**

---

## 🌐 **Servidor de Producción**

### **Plataforma:** [Render](https://render.com)
### **URL Producción:** `https://tijzibackend.onrender.com`
### **Repositorio:** Conectado automáticamente con GitHub

**Dashboard Render:** [https://dashboard.render.com](https://dashboard.render.com)

---

## 🔧 **Configuración Actual**

### **Variables de Entorno en Render:**
```bash
ACCESS_TOKEN = "EAARCZANcIBdYBPE2NUeZBCMCYn92ZBQkZCXYcSXUOXPZBnZCVli9vZB3I5mFHDsmADSlYsQ4RG8lopZBMcRUAzvK7RZABCydPtS6hYhv0SwtA63CPPqh7ZBwZAuPUwZAJ4B5eLxVydo6mzi5bxmIXZCFyPPHbZAKVSLglZCvFrdeKKUZC0yjLRJ45z22fQ3M5LYM1kskurmIjjkbRpUiJ1oWm7UggViB0TQJ9gFrCew5Vk2QpN8QJlL8t48VcwYlIfj9CAZDZD"
PHONE_NUMBER_ID = "466573396530146"
TEMPLATE_NAME = "otp_tijzi"
```

### **Template WhatsApp Activo:**
- **Nombre:** `otp_tijzi`
- **Mensaje:** "Tu código de verificación es *{{1}}*."
- **Idioma:** `es` (Español)
- **Categoría:** `AUTHENTICATION`
- **Botón:** "Copiar código" (funcional)

### **Número de Testing Verificado:**
- **Número:** `+57 300 405 1582`
- **Estado:** ✅ VERIFIED y funcional

---

## 🧪 **Testing del Sistema**

### **1. Verificar Estado del Servidor:**
```bash
curl https://tijzibackend.onrender.com/health
# Respuesta esperada: {"status": "healthy", "service": "tijzi-backend", "version": "1.0.0"}
```

### **2. Verificar Configuración:**
```bash
curl https://tijzibackend.onrender.com/auth/debug-config
# Respuesta esperada: template_name: "otp_tijzi", access_token_configured: true
```

### **3. Testing Completo - Flujo OTP:**

#### **Paso 1: Enviar Código OTP**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"countryCode": "+57", "phoneNumber": "3004051582"}'
```
**Respuesta esperada:** `{"message": "Code sent successfully"}`

#### **Paso 2: Verificar Código Recibido**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"countryCode": "+57", "phoneNumber": "3004051582", "otp": "CODIGO_RECIBIDO"}'
```
**Respuesta esperada:** `{"session_token": "tijzi-token-...", "user_id": "+573004051582"}`

---

## 📱 **WhatsApp Integration**

### **Facebook/Meta Configuration:**
- **WhatsApp Business Account ID:** `436230259575199`
- **Phone Number ID:** `466573396530146`
- **API Version:** `v22.0`
- **Template Category:** `AUTHENTICATION`

### **Templates Disponibles:**
- ✅ `otp_tijzi` - "Tu código de verificación es *{{1}}*." (ACTIVO)
- ✅ `otp_login_whatsapp` - "*{{1}}* es tu código de verificación." + Footer
- ✅ `hello_world` - Template de prueba básico
- ✅ `otp_tijzi_login` - Template en español colombiano (es_CO)

---

## 🏗️ **Arquitectura del Proyecto**

### **Backend (FastAPI + Python):**
```
app/
├── main.py                 # Servidor principal
├── routes/
│   └── auth.py            # Endpoints de autenticación
└── services/
    ├── otp_service.py     # Generación y validación OTP
    └── whatsapp_service.py # (Inline en auth.py)
```

### **Frontend (Kotlin Multiplatform):**
```
shared/
├── domain/
│   ├── model/             # Country, UserSession
│   └── usecase/           # RequestOtpUseCase, VerifyOtpUseCase
├── data/
│   ├── repository/        # AuthRepository, CountryRepository
│   └── remote/            # HttpClient, DTOs
└── presentation/
    ├── model/             # AuthUiState, eventos
    └── viewmodel/         # AuthViewModel
```

---

## ⚡ **Endpoints Disponibles**

### **Endpoints Principales:**
- `POST /auth/send-code` - Enviar código OTP
- `POST /auth/verify-code` - Verificar código OTP

### **Endpoints de Testing:**
- `GET /health` - Estado del servidor
- `GET /auth/debug-config` - Configuración actual
- `POST /test-otp` - Testing OTP sin WhatsApp

### **Endpoints de Desarrollo:**
- `POST /auth/send-code-simulation` - Simulación para desarrollo

---

## 🔍 **Troubleshooting**

### **Problema: "Code sent successfully" pero no llega WhatsApp**
1. Verificar que ACCESS_TOKEN sea válido
2. Confirmar que PHONE_NUMBER_ID sea correcto
3. Verificar que el número esté en formato correcto (573004051582)

### **Problema: "Invalid or expired code"**
1. Usar el código exacto de 6 dígitos recibido
2. Verificar que no hayan pasado más de 5 minutos
3. Usar el mismo número para envío y verificación

### **Problema: "Template does not exist"**
1. Verificar template_name en debug-config
2. Listar templates disponibles con comando Meta API
3. Cambiar TEMPLATE_NAME en Render Dashboard

---

## 🚀 **Próximos Pasos**

### **1. Frontend Kotlin (Prioridad Alta):**
- [ ] Conectar AuthViewModel con backend
- [ ] Testing desde app Android/iOS
- [ ] Implementar UI screens faltantes

### **2. Optimizaciones:**
- [ ] Múltiples templates por caso de uso
- [ ] Rate limiting mejorado
- [ ] Analytics y logging

### **3. Producción:**
- [ ] Números adicionales verificados
- [ ] Monitoring y alertas
- [ ] Backup de configuraciones

---

## 📞 **Comandos Rápidos de Testing**

```bash
# Testing rápido completo
curl https://tijzibackend.onrender.com/health && \
curl -X POST https://tijzibackend.onrender.com/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"countryCode": "+57", "phoneNumber": "3004051582"}'

# Verificar configuración
curl https://tijzibackend.onrender.com/auth/debug-config

# Simular envío para desarrollo
curl -X POST https://tijzibackend.onrender.com/auth/send-code-simulation \
  -H "Content-Type: application/json" \
  -d '{"countryCode": "+57", "phoneNumber": "3001234567"}'
```

---

## 📝 **Notas Importantes**

### **Rate Limiting Activo:**
- Máximo 3 códigos por hora por número
- Mínimo 60 segundos entre solicitudes
- Códigos expiran en 5 minutos

### **Números de Testing:**
- `+57 300 405 1582` - Verificado y funcional
- `+57 305 440 1383` - Estado EXPIRED

### **Credenciales:**
- ACCESS_TOKEN se regenera periódicamente
- PHONE_NUMBER_ID es permanente
- Templates requieren aprobación de Meta

---

## 🎯 **Estado de Desarrollo**

**✅ Completado (100%):**
- Backend FastAPI funcional
- Integración WhatsApp Business API
- Generación y verificación OTP
- Rate limiting
- Validaciones robustas
- Manejo de errores
- Arquitectura KMM preparada

**🔄 En Progreso:**
- Conexión frontend Kotlin
- Testing end-to-end

**📋 Pendiente:**
- Templates adicionales
- Múltiples números verificados
- Analytics y monitoring

---

**Última actualización:** Agosto 2025  
**Estado:** ✅ Sistema funcionando en producción  
**Backend URL:** https://tijzibackend.onrender.com