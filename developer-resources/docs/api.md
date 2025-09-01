# 🔐 **AuthFlow Supabase - Complete API Documentation**

## 📋 **Table of Contents**
- [Overview](#overview)
- [Services Architecture](#services-architecture)
- [Auth Service API](#auth-service-api)
- [Session Service API](#session-service-api)
- [Authentication Flow](#authentication-flow)
- [Request/Response Schemas](#requestresponse-schemas)
- [Error Handling](#error-handling)
- [Security Features](#security-features)
- [Rate Limiting](#rate-limiting)
- [Development & Testing](#development--testing)

---

## 🌟 **Overview**

AuthFlow is a secure, scalable authentication microservice system built with FastAPI and Supabase integration. It consists of two main services:

- **🔐 Auth Service**: Handles user authentication, registration, and password management
- **📱 Session Service**: Manages user sessions, device verification, and Redis-based session storage

**Key Features:**
- 🔐 User registration and authentication via Supabase
- 📱 Device fingerprinting and tracking
- 🗄️ Redis-based session management with TTL
- 🔒 Secure password handling and reset
- 📊 Comprehensive logging and monitoring
- 🚀 Microservices architecture with Docker support

---

## 🏗️ **Services Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App   │────│   Auth Service   │────│   Supabase      │
│                 │    │   (Port 8001)    │    │   (Auth DB)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌──────────────────┐             │
         └──────────────│  Session Service │─────────────┘
                        │   (Port 8000)    │
                        └──────────────────┘
                                │
                                │
                        ┌──────────────────┐
                        │      Redis       │
                        │   (Port 6379)    │
                        └──────────────────┘
```

---

## 🔐 **Auth Service API**

**Base URL:** `http://localhost:8001`  
**API Version:** `v1`  
**Full Base:** `http://localhost:8001/api/v1`

### **🔑 Authentication Endpoints**

#### **1. User Registration**
```http
POST /api/v1/simple_auth/signup
```

**Description:** Register a new user account with email verification

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Sign in successful",
  "data": {
    "message": "Sign up successful! Kindly check your email for verification."
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Failed to sign up! Please try again later.",
  "solution": "If email already exists, please sign in after verifying your email."
}
```

---

#### **2. User Login**
```http
POST /api/v1/simple_auth/signin
```

**Description:** Authenticate existing user and create session

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Sign in successful",
  "data": {
    "session": {
      "session_id": "uuid-string",
      "fingerprint": "device-fingerprint-hash",
      "user_id": 123,
      "info": {
        "user_agent": "Mozilla/5.0...",
        "accept_language": "en-US,en;q=0.9",
        "x_forwarded_for": "192.168.1.100"
      }
    },
    "device_id": 456
  }
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "message": "Failed to sign in! Either email or password is incorrect. Verify your credentials and try again."
}
```

---

#### **3. User Logout**
```http
POST /api/v1/simple_auth/logout
```

**Description:** Terminate user session

**Request Headers:**
```
Cookie: session_id=<session_id>
```

**Response (Success - 200):**
```json
{
  "message": "Logged out successfully"
}
```

---

#### **4. Password Reset Request**
```http
POST /api/v1/simple_auth/forgot-password
```

**Description:** Request password reset link via email

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Password reset email sent successfully"
}
```

---

#### **5. Password Reset Update**
```http
POST /api/v1/simple_auth/reset-password/update
```

**Description:** Update password using reset token

**Request Body:**
```json
{
  "password": "newSecurePassword123!",
  "token": "reset-token-string"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

---

### **🏥 Health Check Endpoints**

#### **6. Service Health**
```http
GET /health
```

**Description:** Check service health status

**Response (Success - 200):**
```json
{
  "status": "ok",
  "message": "Auth service is running",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

### **📱 Session Management Endpoints**

#### **7. Create Session**
```http
POST /api/v1/session/create
```

**Description:** Create new user session with device fingerprinting

**Request Body:**
```json
{
  "user_id": "123"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Session created successfully",
  "data": {
    "session_id": "uuid-string",
    "fingerprint": "device-fingerprint-hash",
    "user_id": 123
  }
}
```

---

#### **8. Delete Session**
```http
DELETE /api/v1/session/delete
```

**Description:** Delete user session

**Request Headers:**
```
Cookie: session_id=<session_id>
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

## 📱 **Session Service API**

**Base URL:** `http://localhost:8000`  
**API Version:** `v1`  
**Full Base:** `http://localhost:8000/api/v1`

### **🔐 Authentication Endpoints**

#### **1. Auth Redirect**
```http
GET /auth/
```

**Description:** Redirects to authentication URL for user login

**Response (Redirect - 307):**
```
Location: <auth_service_url>
```

---

### **📱 Session Management Endpoints**

#### **2. Session Operations**
```http
GET /app/
```

**Description:** Main application route with session verification

**Request Headers:**
```
Cookie: session_id=<session_id>
```

**Response (Success - 200):**
```json
{
  "status": "authenticated",
  "message": "Access granted",
  "user_id": 123
}
```

**Response (Redirect - 307):**
```
Location: <auth_service_url>  # If session invalid
```

---

#### **3. Backend Redirect**
```http
GET /backend/
```

**Description:** Redirects to backend service

**Response (Redirect - 307):**
```
Location: <backend_service_url>
```

---

### **🏥 Health Check Endpoints**

#### **4. Service Health**
```http
GET /health/
```

**Description:** Check session service health status

**Response (Success - 200):**
```json
{
  "status": "ok"
}
```

---

## 🔄 **Authentication Flow**

### **Complete User Journey**

```
1. User Registration
   ┌─────────────────┐
   │ POST /signup    │
   │ Email + Password│
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Email Verification│
   │ (Supabase)      │
   └─────────────────┘
           │
           ▼
2. User Login
   ┌─────────────────┐
   │ POST /signin    │
   │ Email + Password│
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Device          │
   │ Fingerprinting  │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Session Creation│
   │ (Redis)         │
   └─────────────────┘
           │
           ▼
3. Session Usage
   ┌─────────────────┐
   │ Cookie:         │
   │ session_id      │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Device          │
   │ Verification    │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Access Granted  │
   └─────────────────┘
```

---

## 📊 **Request/Response Schemas**

### **User Authentication Schema**
```json
{
  "email": "string (required, valid email format)",
  "password": "string (required, min 8 characters)"
}
```

### **Password Reset Schema**
```json
{
  "password": "string (required, min 8 characters)",
  "token": "string (required, valid reset token)"
}
```

### **Session Schema**
```json
{
  "session_id": "string (UUID format)",
  "fingerprint": "string (SHA-256 hash)",
  "user_id": "integer (user identifier)",
  "created_at": "datetime (ISO format)",
  "expires_at": "datetime (ISO format)"
}
```

### **Device Info Schema**
```json
{
  "user_agent": "string (browser/device identifier)",
  "accept_language": "string (language preference)",
  "x_forwarded_for": "string (IP address)",
  "ip": "string (client IP)",
  "user_id": "integer (user identifier)"
}
```

### **Error Response Schema**
```json
{
  "success": false,
  "message": "string (human-readable error description)",
  "error_code": "string (error identifier)",
  "details": {
    "field": "string (additional error details)"
  }
}
```

---

## ❌ **Error Handling**

### **HTTP Status Codes**
- **200** - Success
- **201** - Created
- **307** - Temporary Redirect
- **400** - Bad Request (validation errors)
- **401** - Unauthorized (authentication failed)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **422** - Unprocessable Entity (schema validation failed)
- **500** - Internal Server Error

### **Common Error Messages**
```json
{
  "EMAIL_INVALID": "Invalid email format",
  "PASSWORD_TOO_SHORT": "Password must be at least 8 characters",
  "USER_NOT_FOUND": "User account not found",
  "INVALID_CREDENTIALS": "Email or password is incorrect",
  "SESSION_EXPIRED": "Session has expired",
  "DEVICE_MISMATCH": "Device fingerprint mismatch",
  "TOKEN_INVALID": "Invalid or expired token",
  "SESSION_NOT_FOUND": "Session does not exist"
}
```

---

## 💡 **API Examples**

### **Complete Authentication Flow**

#### **Step 1: User Registration**
```bash
curl -X POST "http://localhost:8001/api/v1/simple_auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }'
```

#### **Step 2: User Login**
```bash
curl -X POST "http://localhost:8001/api/v1/simple_auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }'
```

#### **Step 3: Using Session with Session Service**
```bash
curl -X GET "http://localhost:8000/app/" \
  -H "Cookie: session_id=<session_id_from_login>"
```

#### **Step 4: User Logout**
```bash
curl -X POST "http://localhost:8001/api/v1/simple_auth/logout" \
  -H "Cookie: session_id=<session_id>"
```

### **Session Service Operations**

#### **Check Session Service Health**
```bash
curl -X GET "http://localhost:8000/health/"
```

#### **Access Protected Route**
```bash
curl -X GET "http://localhost:8000/app/" \
  -H "Cookie: session_id=<valid_session_id>"
```

---

## 🚦 **Rate Limiting**

**Current Limits (Handled at Nginx Level):**
- **Authentication endpoints**: 5 requests per minute per IP
- **Password reset**: 3 requests per hour per email
- **General API**: 100 requests per minute per IP
- **Session operations**: 50 requests per minute per session

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642233600
```

---

## 🔒 **Security Features**

### **Device Fingerprinting**
- **SHA-256 hashing** of device characteristics
- **IP address tracking** with X-Forwarded-For support
- **User agent analysis** for device identification
- **Language preference** tracking
- **Session binding** to prevent hijacking

### **Session Security**
- **UUID-based session IDs** for uniqueness
- **Redis storage** with configurable TTL expiration
- **Device binding** to prevent session hijacking
- **Automatic cleanup** of expired sessions
- **Fingerprint validation** on each request

### **Password Security**
- **Supabase integration** for secure password handling
- **Email verification** required for new accounts
- **Secure token generation** for password resets
- **Rate limiting** on authentication attempts
- **Password complexity** requirements

### **Infrastructure Security**
- **HTTPS enforcement** in production
- **CORS configuration** for cross-origin requests
- **Input validation** with Pydantic schemas
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** with proper output encoding

---

## 🚀 **Development & Testing**

### **Environment Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd authflow-supabase

# Install dependencies
pip install -r auth-service/requirements.txt
pip install -r session-service/requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env with your configuration
```

### **Running Services**
```bash
# Start with Docker Compose
docker-compose up -d

# Or run individually
cd auth-service && python main.py
cd session-service && python main.py
```

### **Testing the APIs**
```bash
# Test Auth Service
curl http://localhost:8001/health
curl http://localhost:8001/docs  # Swagger UI

# Test Session Service
curl http://localhost:8000/health/
```

### **Running Tests**
```bash
# Auth Service Tests
cd auth-service
pytest . --cov=auth-service --cov-report=html

# Session Service Tests
cd session-service
pytest . --cov=session-service --cov-report=html
```

---

## 📚 **Additional Resources**

### **Interactive Documentation**
- **Auth Service Swagger UI**: `http://localhost:8001/docs`
- **Auth Service ReDoc**: `http://localhost:8001/redoc`
- **Auth Service OpenAPI**: `http://localhost:8001/openapi.json`

### **Monitoring & Logs**
- **Auth Service Logs**: `auth-service/auth-service.log`
- **Session Service Logs**: `session-service/session-service.log`
- **Test Coverage**: `htmlcov/index.html`

### **Configuration Files**
- **Environment Template**: `env.template`
- **Docker Compose**: `docker-compose.yml`
- **Docker Files**: `auth-service/Dockerfile`, `session-service/Dockerfile`

---

## 🤝 **Support & Contact**

**Developer Team:** Eorix  
**Email:** contact@eorix.io  
**Website:** https://eorix.io  
**Repository:** [Your GitHub Repo URL]

---

## 📝 **Changelog**

### **Version 1.0.0 (Current)**
- ✅ User authentication with Supabase
- ✅ Session management with Redis
- ✅ Device fingerprinting
- ✅ Password reset functionality
- ✅ Comprehensive API documentation
- ✅ Docker containerization
- ✅ Test coverage >90%
- ✅ Security scanning with Bandit

### **Planned Features**
- 🔄 OAuth integration (Google, GitHub)
- 🔄 Multi-factor authentication
- 🔄 Role-based access control
- 🔄 API rate limiting middleware
- 🔄 Advanced monitoring and metrics

---

*Last Updated: January 2024*  
*API Version: 1.0.0*  
*Documentation Version: 2.0*  
*Services: Auth Service (v1.0.0), Session Service (v1.0.0)*
