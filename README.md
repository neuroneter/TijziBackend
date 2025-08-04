# 🚀 Tijzi Backend - Sistema OTP Multi-idioma

Sistema completo de autenticación OTP vía **WhatsApp** y **SMS** con soporte para **5 idiomas**.

## 📋 **Estado del Proyecto (Actualizado: Agosto 2025)**

✅ **Backend funcionando al 100%**  
✅ **WhatsApp Business API multi-idioma**  
✅ **SMS con auto-detección optimizada**  
✅ **5 idiomas soportados**  
✅ **API unificada y verificación automática**

---

## 🌐 **Servidor de Producción**

### **Plataforma:** [Render](https://render.com)
### **URL Producción:** `https://tijzibackend.onrender.com`
### **Repositorio:** Conectado automáticamente con GitHub

---

## 🌍 **Idiomas Soportados**

| Código | Idioma    | WhatsApp Template | SMS Optimizado |
|--------|-----------|-------------------|----------------|
| `es`   | Español   | `otp_tijzi_es`    | ✅ Auto-detección |
| `en`   | English   | `otp_tijzi_en`    | ✅ Auto-detección |
| `pt`   | Português | `otp_tijzi_pt`    | ✅ Auto-detección |
| `it`   | Italiano  | `otp_tijzi_it`    | ✅ Auto-detección |
| `fr`   | Français  | `otp_tijzi_fr`    | ✅ Auto-detección |

---

## 🔧 **Configuración de Variables de Entorno**

### **En Render Dashboard → Environment:**

#### **WhatsApp Business API:**
```bash
ACCESS_TOKEN = "EAARCZANcIBdYBPE2NUeZBCMCYn92ZBQkZCXYcSXUOXPZBnZCVli9vZB3I5mFHDsmADSlYsQ4RG8lopZBMcRUAzvK7RZABCydPtS6hYhv0SwtA63CPPqh7ZBwZAuPUwZAJ4B5eLxVydo6mzi5bxmIXZCFyPPHbZAKVSLglZCvFrdeKKUZC0yjLRJ45z22fQ3M5LYM1kskurmIjjkbRpUiJ1oWm7UggViB0TQJ9gFrCew5Vk2QpN8QJlL8t48VcwYlIfj9CAZDZD"
PHONE_NUMBER_ID = "466573396530146"
TEMPLATE_NAME = "otp_tijzi"
```

#### **SMS Multi-idioma (Twilio):**
```bash
TWILIO_ACCOUNT_SID = "ACcc370ead9b95f047020572ddfa2d3b72"
TWILIO_AUTH_TOKEN = "2b179f9bce8d3bd362c37bffed2d9e5a"
TWILIO_VERIFY_SERVICE_SID = "VA23ba10dd7b3dff7a3d6bba5b31dc5304"
TWILIO_PHONE_NUMBER = "+1234567890"
```

---

## 📱 **Canales Disponibles**

### **🟢 WhatsApp Business API**
- **Formato:** Template con botón "Copiar código"
- **Templates por idioma:** Cada idioma tiene su template específico
- **Experiencia:** Mensaje profesional + botón para copiar código
- **Auto-detección:** No necesaria (botón integrado)

### **🟢 SMS con Auto-detección**
- **Formato:** Mensaje optimizado para iOS/Android
- **Detección automática:** Sistemas operativos detectan códigos automáticamente
- **Experiencia:** "Se detectó código de verificación" → auto-fill
- **Provider:** Twilio SMS básico

---

## 🚀 **API Endpoints**

### **📋 Ver idiomas soportados:**
```bash
GET /auth/supported-languages
```

**Respuesta:**
```json
{
  "supported_languages": [
    {
      "code": "es",
      "name": "Español",
      "whatsapp_template": "otp_tijzi_es",
      "sms_sample": "123456 es tu código de verificación de Tijzi. Válido por 5 minutos."
    }
  ],
  "total_languages": 5,
  "default_language": "es"
}
```

### **📤 Enviar Código OTP (Multi-idioma):**
```bash
POST /auth/send-otp-multilingual
```

**Request Body:**
```json
{
  "channel": "whatsapp|sms",
  "countryCode": "+57",
  "phoneNumber": "3004051582", 
  "language": "es|en|pt|it|fr"
}
```

**Response exitoso:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "channel": "whatsapp",
  "language": "es",
  "language_name": "Español",
  "template": "otp_tijzi_es",
  "recipient": "+573004051582",
  "expires_in": "5 minutes"
}
```

### **✅ Verificar Código OTP (Universal):**
```bash
POST /auth/verify-code
```

**Request Body:**
```json
{
  "countryCode": "+57",
  "phoneNumber": "3004051582",
  "otp": "123456"
}
```

**Response exitoso:**
```json
{
  "message": "Code verified successfully",
  "session_token": "tijzi-token-+573004051582-1754171001",
  "user_id": "+573004051582",
  "method": "Internal OTP System"
}
```

---

## 🧪 **Ejemplos de Testing**

### **🇪🇸 WhatsApp en Español:**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/send-otp-multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "whatsapp",
    "countryCode": "+57",
    "phoneNumber": "3004051582",
    "language": "es"
  }'
```

**Mensaje WhatsApp:** *"Tu código de verificación es **123456**."* + Botón "Copiar código"

### **🇺🇸 SMS en English:**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/send-otp-multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "sms",
    "countryCode": "+57", 
    "phoneNumber": "3004051582",
    "language": "en"
  }'
```

**Mensaje SMS:** *"123456 is your Tijzi verification code. Valid for 5 minutes."*
**Auto-detección:** iOS/Android detectan automáticamente y ofrecen auto-fill

### **🇧🇷 SMS en Português:**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/send-otp-multilingual \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "sms",
    "countryCode": "+57",
    "phoneNumber": "3004051582", 
    "language": "pt"
  }'
```

**Mensaje SMS:** *"123456 é seu código de verificação Tijzi. Válido por 5 minutos."*

### **✅ Verificar cualquier código:**
```bash
curl -X POST https://tijzibackend.onrender.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{
    "countryCode": "+57",
    "phoneNumber": "3004051582",
    "otp": "123456"
  }'
```

---

## 🔍 **Endpoints de Diagnóstico**

### **🏥 Estado del servidor:**
```bash
GET /health
# Respuesta: {"status": "healthy", "service": "tijzi-backend", "version": "1.0.0"}
```

### **📊 Estado de canales:**
```bash
GET /auth/available-channels
```

**Respuesta:**
```json
{
  "available_channels": [
    {
      "id": "whatsapp",
      "name": "WhatsApp", 
      "description": "Código vía WhatsApp con botón copiar",
      "reliability": "Alta"
    },
    {
      "id": "sms",
      "name": "SMS",
      "description": "Código vía mensaje de texto con auto-detección",
      "reliability": "Alta"
    }
  ],
  "total_configured": 2,
  "default_channel": "whatsapp"
}
```

### **🔧 Debug WhatsApp:**
```bash
GET /auth/debug-config
```

### **📱 Debug SMS:**
```bash
GET /auth/sms-debug
```

---

## 🎯 **Mensajes por Idioma**

### **📱 Mensajes SMS (Auto-detección optimizada):**

| Idioma | Mensaje |
|--------|---------|
| **🇪🇸 Español** | `123456 es tu código de verificación de Tijzi. Válido por 5 minutos.` |
| **🇺🇸 English** | `123456 is your Tijzi verification code. Valid for 5 minutes.` |
| **🇧🇷 Português** | `123456 é seu código de verificação Tijzi. Válido por 5 minutos.` |
| **🇮🇹 Italiano** | `123456 è il tuo codice di verifica Tijzi. Valido per 5 minuti.` |
| **🇫🇷 Français** | `123456 est votre code de vérification Tijzi. Valide 5 minutes.` |

### **💬 Templates WhatsApp:**

| Idioma | Template Name | Mensaje |
|--------|---------------|---------|
| **🇪🇸 Español** | `otp_tijzi_es` | *"Tu código de verificación es **{{1}}**."* |
| **🇺🇸 English** | `otp_tijzi_en` | *"Your verification code is **{{1}}**."* |
| **🇧🇷 Português** | `otp_tijzi_pt` | *"Seu código de verificação é **{{1}}**."* |
| **🇮🇹 Italiano** | `otp_tijzi_it` | *"Il tuo codice di verifica è **{{1}}**."* |
| **🇫🇷 Français** | `otp_tijzi_fr` | *"Votre code de vérification est **{{1}}**."* |

---

## 🛠️ **Configuración de Desarrollo**

### **Requisitos:**
- Python 3.9+
- FastAPI
- Cuenta Meta Business (para WhatsApp)
- Cuenta Twilio (para SMS)

### **Setup Local:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Variables de entorno (.env)
cp .env.example .env
# Completar con tus credenciales

# Ejecutar servidor
uvicorn app.main:app --reload --port 8000
```

### **Testing Local:**
```bash
# Verificar servidor
curl http://localhost:8000/health

# Ver idiomas
curl http://localhost:8000/auth/supported-languages

# Test envío
curl -X POST http://localhost:8000/auth/send-otp-multilingual \
  -H "Content-Type: application/json" \
  -d '{"channel": "sms", "countryCode": "+57", "phoneNumber": "3001234567", "language": "es"}'
```

---

## 📱 **Integración Frontend**

### **JavaScript/TypeScript:**
```javascript
// Función para enviar OTP
async function sendOTP(channel, phone, language) {
  const response = await fetch('/auth/send-otp-multilingual', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      channel: channel,        // "whatsapp" o "sms"
      countryCode: "+57",
      phoneNumber: phone,
      language: language       // "es", "en", "pt", "it", "fr"
    })
  });
  return response.json();
}

// Función para verificar código
async function verifyOTP(phone, code) {
  const response = await fetch('/auth/verify-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      countryCode: "+57",
      phoneNumber: phone,
      otp: code
    })
  });
  return response.json();
}

// Ejemplo de uso
sendOTP("whatsapp", "3004051582", "es")
  .then(result => console.log("Código enviado:", result));
```

### **Kotlin Multiplatform:**
```kotlin
data class OtpRequest(
    val channel: String,
    val countryCode: String,
    val phoneNumber: String,
    val language: String
)

data class VerifyRequest(
    val countryCode: String,
    val phoneNumber: String,
    val otp: String
)

suspend fun sendOtp(channel: String, phone: String, language: String) {
    val request = OtpRequest(
        channel = channel,
        countryCode = "+57",
        phoneNumber = phone,
        language = language
    )
    
    val response = httpClient.post("/auth/send-otp-multilingual") {
        contentType(ContentType.Application.Json)
        setBody(request)
    }
}

suspend fun verifyOtp(phone: String, code: String) {
    val request = VerifyRequest(
        countryCode = "+57",
        phoneNumber = phone,
        otp = code
    )
    
    val response = httpClient.post("/auth/verify-code") {
        contentType(ContentType.Application.Json)
        setBody(request)
    }
}
```

---

## 🔒 **Seguridad y Limitaciones**

### **🛡️ Rate Limiting:**
- **WhatsApp:** 3 códigos por hora por número
- **SMS:** 3 códigos por hora por número
- **Verificación:** Mínimo 60 segundos entre solicitudes

### **⏰ Expiración:**
- **Códigos:** 5 minutos de validez
- **Tokens de sesión:** Configurable

### **🔐 Validaciones:**
- Formato de número de teléfono
- Códigos de 6 dígitos
- Validación de idioma soportado
- Verificación de canal válido

---

## 🚨 **Troubleshooting**

### **❌ Error: "Invalid language"**
**Solución:** Usar solo idiomas soportados: `es`, `en`, `pt`, `it`, `fr`

### **❌ Error: "Failed to send WhatsApp"**
**Causas comunes:**
- ACCESS_TOKEN expirado (renovar cada 24h)
- Template no aprobado en Meta Business Manager
- Número destino en formato incorrecto

### **❌ Error: "Failed to send SMS"**
**Causas comunes:**
- TWILIO_PHONE_NUMBER no configurado
- Número Twilio inválido
- Saldo insuficiente en Twilio

### **❌ Error: "Invalid or expired code"**
**Causas comunes:**
- Código expirado (>5 minutos)
- Código incorrecto
- Múltiples intentos de verificación

---

## 📊 **Métricas y Monitoreo**

### **📈 Logs de Interés:**
- `🔥 [WhatsApp]` - Eventos de WhatsApp
- `🔥 [SMS]` - Eventos de SMS
- `🔥 [OTP Multi]` - Eventos multi-idioma
- `🔥 [Verify]` - Eventos de verificación

### **🎯 KPIs:**
- Tasa de entrega por canal
- Tasa de verificación exitosa
- Distribución de idiomas usados
- Tiempo promedio de verificación

---

## 🚀 **Roadmap**

### **🟡 Próximas mejoras:**
- [ ] Analytics detallados por idioma
- [ ] Webhook para estados de entrega
- [ ] Templates dinámicos WhatsApp
- [ ] Soporte para más canales (Email, Push)

### **🟢 Completado:**
- [x] Sistema multi-idioma (5 idiomas)
- [x] WhatsApp Business API con templates
- [x] SMS con auto-detección optimizada
- [x] API unificada y verificación automática
- [x] Rate limiting y seguridad

---

## 📞 **Soporte**

Para problemas o preguntas:
- **Logs detallados:** Render Dashboard → tijzibackend → Logs
- **Status en tiempo real:** `GET /health`
- **Configuración:** `GET /auth/debug-config`

---

## 🎉 **Sistema Listo para Producción**

**✅ Multi-idioma completo**  
**✅ Experiencia de usuario optimizada**  
**✅ Auto-detección en dispositivos móviles**  
**✅ API robusta y escalable**

**Última actualización:** Agosto 2025  
**Backend URL:** https://tijzibackend.onrender.com  
**Canales:** WhatsApp ✅ | SMS ✅ | 5 idiomas ✅