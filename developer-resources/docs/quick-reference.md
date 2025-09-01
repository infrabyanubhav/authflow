# 🚀 **AuthFlow Supabase - Quick Reference Guide**

## 📍 **Service URLs**

| Service | URL | Port | Health Check |
|---------|-----|-------|--------------|
| **Auth Service** | `http://localhost:8001` | 8001 | `/health` |
| **Session Service** | `http://localhost:8000` | 8000 | `/health/` |
| **Redis** | `localhost` | 6379 | `redis-cli ping` |

---

## 🔑 **Essential API Endpoints**

### **Authentication (Auth Service)**
```bash
# User Registration
POST /api/v1/simple_auth/signup
Body: {"email": "user@example.com", "password": "password123"}

# User Login
POST /api/v1/simple_auth/signin
Body: {"email": "user@example.com", "password": "password123"}

# User Logout
POST /api/v1/simple_auth/logout
Headers: Cookie: session_id=<session_id>

# Password Reset
POST /api/v1/simple_auth/forgot-password
Body: {"email": "user@example.com"}

# Update Password
POST /api/v1/simple_auth/reset-password/update
Body: {"password": "newpass", "token": "reset_token"}
```

### **Session Management (Session Service)**
```bash
# Check Session
GET /app/
Headers: Cookie: session_id=<session_id>

# Health Check
GET /health/

# Auth Redirect
GET /auth/

# Backend Redirect
GET /backend/
```

---

## 🧪 **Testing Commands**

### **Quick Health Checks**
```bash
# Auth Service
curl http://localhost:8001/health

# Session Service
curl http://localhost:8000/health/

# Redis
redis-cli ping
```

### **Complete Authentication Flow Test**
```bash
# 1. Register User
curl -X POST "http://localhost:8001/api/v1/simple_auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# 2. Login User
curl -X POST "http://localhost:8001/api/v1/simple_auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# 3. Use Session (extract session_id from login response)
curl -X GET "http://localhost:8000/app/" \
  -H "Cookie: session_id=<session_id>"

# 4. Logout
curl -X POST "http://localhost:8001/api/v1/simple_auth/logout" \
  -H "Cookie: session_id=<session_id>"
```

---

## 🐳 **Docker Commands**

### **Start Services**
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d auth-service
docker-compose up -d session-service

# View logs
docker-compose logs -f auth-service
docker-compose logs -f session-service
```

### **Stop Services**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🧪 **Testing & Development**

### **Run Tests**
```bash
# Auth Service Tests
cd auth-service
pytest . --cov=auth-service --cov-report=html

# Session Service Tests
cd session-service
pytest . --cov=session-service --cov-report=html
```

### **Code Quality**
```bash
# Lint and format
cd auth-service
./lint.sh

cd session-service
./lint.sh
```

### **Database Migrations**
```bash
# Run migrations
cd auth-service
./migrate.sh
```

---

## 🔧 **Environment Variables**

### **Required Variables**
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Security
SESSION_SECRET_KEY=your_secret_key
```

---

## 📚 **Useful URLs**

| Purpose | URL |
|---------|-----|
| **Auth Service Docs** | `http://localhost:8001/docs` |
| **Auth Service ReDoc** | `http://localhost:8001/redoc` |
| **Session Service Health** | `http://localhost:8000/health/` |
| **Test Coverage** | `htmlcov/index.html` |

---

## 🚨 **Common Issues & Solutions**

### **Service Won't Start**
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :8001
lsof -i :6379

# Check Docker containers
docker ps -a
docker-compose logs
```

### **Database Connection Issues**
```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping
```

### **Session Issues**
```bash
# Check Redis keys
redis-cli keys "*session*"

# Clear Redis
redis-cli flushall
```

---

## 📱 **Device Fingerprinting**

### **Fingerprint Components**
- IP Address
- User Agent
- Accept Language
- X-Forwarded-For header

### **Fingerprint Generation**
```python
# SHA-256 hash of: ip|user_agent|accept_language
fingerprint = hashlib.sha256(f"{ip}|{ua}|{lang}".encode()).hexdigest()
```

---

## 🔒 **Security Checklist**

- [ ] HTTPS enabled in production
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] Session TTL configured
- [ ] Device fingerprinting enabled
- [ ] Error messages don't leak information
- [ ] CORS properly configured
- [ ] Secrets stored in environment variables

---

## 📞 **Support**

**Team:** INFRABYANUBHAV | CYBERSOLININC
**Email:** infrabyanubhav@gmail.com | cybersolininc@gmail.com 
**Docs:** Check `developer-resources/docs/` folder

---

*Quick Reference v1.0 - Keep this handy for development! 🚀*
