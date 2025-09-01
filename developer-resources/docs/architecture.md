# 🏗️ **AuthFlow Supabase - System Architecture**

## 📋 **Table of Contents**
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Service Components](#service-components)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Technology Stack](#technology-stack)
- [Deployment Architecture](#deployment-architecture)
- [Scalability & Performance](#scalability--performance)

---

## 🌟 **Overview**

AuthFlow is a secure, microservices-based authentication system designed with a **verification gateway pattern**. The system consists of three main components:

1. **🔐 Auth Service**: Handles user authentication, registration, and session creation
2. **🛡️ Verification Service**: Acts as a gateway, validating sessions and device fingerprints
3. **🚀 Backend Services**: Protected services that require valid authentication

**Key Design Principles:**
- **Gateway Pattern**: Single entry point for all backend requests
- **Session Validation**: Every request validated against Redis sessions
- **Device Fingerprinting**: SHA-256 based device identification
- **Zero Trust**: No request bypasses verification
- **Stateless Authentication**: Session-based with Redis storage

---

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App   │────│ Verification     │────│   Backend      │
│                 │    │   Service        │    │   Services     │
│                 │    │   (Gateway)      │    │   (Protected)  │
│                 │    │   Port 8000      │    │                │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌──────────────────┐             │
         └──────────────│   Auth Service   │─────────────┘
                        │   Port 8001      │
                        └──────────────────┘
                                │
                                │
                        ┌──────────────────┐
                        │      Redis       │
                        │   Port 6379      │
                        └──────────────────┘
```

---

## 🔧 **Service Components**

### **1. 🔐 Auth Service (Port 8001)**

**Primary Responsibilities:**
- User registration and authentication
- Password management and reset
- Session creation and management
- Device fingerprinting and storage
- Supabase integration

**Key Features:**
- **User Management**: Registration, login, logout
- **Session Creation**: Generates UUID-based session IDs
- **Device Tracking**: Creates device fingerprints
- **Password Security**: Handles password resets via Supabase
- **Email Verification**: Manages email verification flow

**API Endpoints:**
```
POST /api/v1/simple_auth/signup     # User registration
POST /api/v1/simple_auth/signin     # User login
POST /api/v1/simple_auth/logout     # User logout
POST /api/v1/simple_auth/forgot-password  # Password reset
POST /api/v1/simple_auth/reset-password/update  # Update password
GET  /health                        # Health check
```

---

### **2. 🛡️ Verification Service (Port 8000)**

**Primary Responsibilities:**
- **Gateway Function**: Intercepts all backend requests
- **Session Validation**: Verifies session existence and validity
- **Device Fingerprinting**: Validates device fingerprint matches
- **Request Routing**: Forwards valid requests to backend
- **Authentication Redirect**: Redirects invalid requests to auth service

**Key Features:**
- **Request Interception**: Catches all incoming requests
- **Session Verification**: Checks Redis for valid sessions
- **Fingerprint Validation**: Ensures device consistency
- **Smart Routing**: Routes based on authentication status
- **Security Enforcement**: Prevents unauthorized access

**API Endpoints:**
```
GET  /app/                         # Main app route (protected)
GET  /auth/                        # Redirect to auth service
GET  /backend/                     # Redirect to backend
GET  /health/                      # Health check
```

---

### **3. 🗄️ Redis (Port 6379)**

**Primary Responsibilities:**
- Session storage and management
- Device fingerprint storage
- User ID caching for quick DB operations
- TTL-based session expiration
- High-performance data caching

**Data Structures:**
- **Sessions**: `session:{session_id}` → session data
- **Device Info**: `device:{user_id}` → device fingerprint
- **User Sessions**: `user_sessions:{user_id}` → active sessions
- **User ID Cache**: `user_id:{session_id}` → user_id for quick DB lookups
- **User Profile Cache**: `user_profile:{user_id}` → frequently accessed user data

**TTL Configuration:**
- **Session TTL**: 3600 seconds (1 hour)
- **Device TTL**: 86400 seconds (24 hours)
- **User ID Cache TTL**: 7200 seconds (2 hours)
- **User Profile Cache TTL**: 1800 seconds (30 minutes)
- **Auto-cleanup**: Expired sessions automatically removed

---

## 🔄 **Data Flow**

### **1. User Authentication Flow**

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│   Client    │───▶│ Auth Service │───▶│   Supabase   │───▶│   Redis     │
│             │    │              │    │              │    │             │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │              ┌──────────────┐         │                   │
       └──────────────│ Verification │◀────────┼───────────────────┘
                      │   Service    │
                      └──────────────┘
```

**Step-by-Step Process:**
1. **Client Request**: User submits login credentials
2. **Auth Service**: Validates credentials with Supabase
3. **Session Creation**: Creates session with device fingerprint
4. **Redis Storage**: Stores session data in Redis
5. **Response**: Returns session ID to client
6. **Verification Ready**: Verification service can now validate requests

---

### **2. Request Verification Flow**

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│   Client    │───▶│ Verification │───▶│   Redis      │───▶│   Backend   │
│             │    │   Service    │    │   (Session   │    │   Service   │
│             │    │   (Gateway)  │    │   Check)     │    │             │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │              ┌──────────────┐         │                   │
       └──────────────│ Auth Service │◀────────┼───────────────────┘
                      │ (Redirect)   │
                      └──────────────┘
```

**Verification Process:**
1. **Request Interception**: Verification service catches all requests
2. **Session Check**: Validates session ID from cookies
3. **Fingerprint Validation**: Ensures device fingerprint matches
4. **Decision Making**:
   - ✅ **Valid**: Forward to backend service
   - ❌ **Invalid**: Redirect to auth service
   - ⏰ **Expired**: Clear session and redirect to auth

---

### **3. Session Validation Logic**

```python
async def validate_request(session_id: str, device_info: dict):
    # 1. Check if session exists in Redis
    session = await redis.get_session(session_id)
    if not session:
        return "REDIRECT_TO_AUTH"
    
    # 2. Check if session is expired
    if session.expired:
        await redis.delete_session(session_id)
        return "REDIRECT_TO_AUTH"
    
    # 3. Validate device fingerprint
    stored_fingerprint = session.device_fingerprint
    current_fingerprint = generate_fingerprint(device_info)
    
    if stored_fingerprint != current_fingerprint:
        return "REDIRECT_TO_AUTH"
    
    # 4. All validations passed
    return "FORWARD_TO_BACKEND"
```

---

## 🔒 **Security Architecture**

### **1. Multi-Layer Security**

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                           │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Verification Service                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Session Check   │  │ Fingerprint     │  │ Rate        │ │
│  │ (Redis)         │  │ Validation      │  │ Limiting    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend Services                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Business Logic  │  │ Data Access     │  │ API         │ │
│  │                 │  │ Layer           │  │ Endpoints   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **2. Security Features**

#### **Session Security**
- **UUID Generation**: Cryptographically secure session IDs
- **TTL Enforcement**: Automatic session expiration
- **Device Binding**: Sessions tied to specific devices
- **Redis Security**: Password-protected Redis instance

#### **Device Fingerprinting**
- **SHA-256 Hashing**: Secure fingerprint generation
- **Multi-Factor**: IP, User-Agent, Language, Headers
- **Tamper Detection**: Prevents session hijacking
- **Consistency Check**: Every request validated

#### **Request Security**
- **Gateway Pattern**: Single point of control
- **Zero Trust**: No request bypasses verification
- **Rate Limiting**: Nginx-level protection
- **Input Validation**: Pydantic schema validation

---

## 🛠️ **Technology Stack**

### **Backend Framework**
- **FastAPI**: Modern, fast web framework
- **Python 3.10+**: High-performance Python runtime
- **Async/Await**: Non-blocking I/O operations

### **Database & Storage**
- **PostgreSQL**: Primary database (via Supabase)
- **Redis**: Session storage and caching
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management

### **Authentication & Security**
- **Supabase**: Authentication provider
- **JWT**: Token-based authentication
- **SHA-256**: Device fingerprinting
- **Fernet**: Encryption for sensitive data

### **Infrastructure**
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and rate limiting
- **PostgreSQL**: Database server

---

## 🚀 **Deployment Architecture**

### **Development Environment**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local Dev     │    │   Docker         │    │   Services      │
│   Environment   │────│   Compose        │────│   (Ports)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────┐
                    │   Port Mapping   │
                    │ 8000 → 8000      │
                    │ 8001 → 8001      │
                    │ 6379 → 6379      │
                    └──────────────────┘
```

### **Production Environment**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Nginx          │    │   Services      │
│   (Cloud)       │────│   (Rate Limiting)│────│   (Containers)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────┐
                    │   Health Checks  │
                    │   Monitoring     │
                    │   Logging        │
                    └──────────────────┘
```

---

## 📈 **Scalability & Performance**

### **1. Horizontal Scaling**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Verification   │    │   Redis Cluster │
│                 │────│   Service        │────│                 │
│                 │    │   Instances      │    │                 │
│                 │    │   (Multiple)     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌──────────────────┐             │
         └──────────────│   Auth Service   │─────────────┘
                        │   Instances      │
                        │   (Multiple)     │
                        └──────────────────┘
```

### **2. Performance Optimizations**

#### **Redis Optimizations**
- **Connection Pooling**: Reuse Redis connections
- **Pipeline Operations**: Batch Redis commands
- **Memory Management**: Optimized data structures
- **TTL Strategy**: Efficient expiration handling
- **User ID Caching**: Quick session-to-user mapping

#### **Service Optimizations**
- **Async Operations**: Non-blocking I/O
- **Caching Strategy**: Redis-based caching
- **Connection Reuse**: HTTP connection pooling
- **Resource Management**: Efficient memory usage
- **Database Optimization**: Cached user IDs reduce DB queries

---

## 🔍 **Monitoring & Observability**

### **1. Health Checks**
- **Service Health**: `/health` endpoints
- **Redis Connectivity**: Connection status
- **Database Status**: PostgreSQL connectivity
- **Response Times**: API performance metrics

### **2. Logging Strategy**
- **Structured Logging**: JSON format logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Tracking**: Unique request IDs
- **Performance Metrics**: Response time logging

### **3. Metrics Collection**
- **Request Counts**: Total requests per endpoint
- **Error Rates**: Failed request percentages
- **Response Times**: Average response times
- **Session Metrics**: Active sessions count

---

## 🚨 **Error Handling & Resilience**

### **1. Circuit Breaker Pattern**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
```

### **2. Fallback Strategies**
- **Redis Unavailable**: Fallback to database sessions
- **Auth Service Down**: Redirect to cached auth page
- **Database Issues**: Use Redis as primary storage
- **Network Problems**: Retry with exponential backoff

---

## 🚀 **User ID Caching Strategy**

### **1. Quick Database Operations**

The system implements intelligent user ID caching to optimize database operations:

```python
# User ID Caching Flow
async def get_user_id_from_session(session_id: str):
    # 1. Check Redis cache first
    cached_user_id = await redis.get(f"user_id:{session_id}")
    if cached_user_id:
        return cached_user_id
    
    # 2. Fallback to session data
    session_data = await redis.get(f"session:{session_id}")
    if session_data:
        user_id = session_data.get("user_id")
        # Cache for future requests
        await redis.setex(f"user_id:{session_id}", 7200, user_id)
        return user_id
    
    return None
```

### **2. Caching Benefits**

- **Reduced DB Queries**: User ID lookups from cache instead of database
- **Faster Response Times**: Sub-millisecond user ID retrieval
- **Scalability**: Handles high-frequency requests efficiently
- **Cost Optimization**: Reduces database load and costs

### **3. Cache Invalidation Strategy**

- **Session Expiry**: User ID cache expires with session
- **Profile Updates**: User profile cache invalidated on changes
- **TTL Management**: Different TTLs for different data types
- **Memory Efficiency**: Automatic cleanup of expired cache entries

---

## 🔮 **Future Architecture Enhancements**

### **1. Planned Improvements**
- **OAuth Integration**: Google, GitHub, Microsoft
- **Multi-Factor Authentication**: TOTP, SMS, Email
- **Role-Based Access Control**: User permissions
- **API Gateway**: Advanced routing and filtering

### **2. Scalability Features**
- **Kubernetes Deployment**: Container orchestration
- **Service Mesh**: Istio for service communication
- **Distributed Tracing**: Jaeger integration
- **Metrics Dashboard**: Grafana + Prometheus

---

## 📚 **Architecture Decisions**

### **1. Why Gateway Pattern?**
- **Centralized Security**: Single point of control
- **Easy Maintenance**: Security logic in one place
- **Scalability**: Can scale verification independently
- **Monitoring**: Centralized request tracking

### **2. Why Redis for Sessions?**
- **Performance**: Sub-millisecond response times
- **TTL Support**: Automatic expiration
- **Persistence**: Data survives restarts
- **Clustering**: Horizontal scaling support

### **3. Why Device Fingerprinting?**
- **Security**: Prevents session hijacking
- **User Experience**: Seamless device switching
- **Compliance**: GDPR and security requirements
- **Monitoring**: Detect suspicious activities

---

## 🤝 **Integration Points**

### **1. External Services**
- **Supabase**: Authentication provider
- **Email Service**: Password reset notifications
- **Monitoring**: Health check endpoints
- **Logging**: Centralized log aggregation

### **2. Internal Services**
- **Backend APIs**: Protected business logic
- **User Management**: Profile and preferences
- **Analytics**: User behavior tracking
- **Admin Panel**: System administration

---

*Architecture Documentation v1.0 - System Design & Implementation Guide 🏗️*
