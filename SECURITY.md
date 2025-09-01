# 🔐 Security Checklist for AuthFlow Supabase

## ⚠️ CRITICAL: Before Making Repository Public

### **1. Remove Sensitive Files from Git History**
```bash
# Remove encryption key
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch auth-service/key_store/key.txt" \
  --prune-empty --tag-name-filter cat -- --all

# Remove environment files
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch *.env" \
  --prune-empty --tag-name-filter cat -- --all

# Remove log files
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch *.log" \
  --prune-empty --tag-name-filter cat -- --all
```

### **2. Verify No Sensitive Data is Committed**
- [ ] No `.env` files in repository
- [ ] No `key_store/key.txt` in repository
- [ ] No log files with sensitive data
- [ ] No hardcoded passwords or API keys
- [ ] No database credentials in code

### **3. Environment Setup**
- [ ] Use `env.template` as base for `.env` files
- [ ] Never commit actual `.env` files
- [ ] Use environment variables for all secrets
- [ ] Generate new encryption keys for production

## 🔒 Security Best Practices

### **1. Key Management**
- [ ] Use environment variables for all secrets
- [ ] Generate unique keys per environment
- [ ] Rotate keys regularly
- [ ] Use secure key storage (HashiCorp Vault, AWS Secrets Manager)

### **2. Environment Variables**
```bash
# Required environment variables
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
REDIS_PASSWORD=your_redis_password
DATABASE_URL=postgresql://username:password@localhost:5432/authflow_db
SESSION_SECRET_KEY=your_session_secret_key
```

### **3. Production Security**
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add security headers
- [ ] Enable CORS properly
- [ ] Use secure session management

## 🚨 Security Checklist

### **Before Each Commit:**
- [ ] No secrets in code
- [ ] No hardcoded credentials
- [ ] No sensitive data in logs
- [ ] All environment files ignored
- [ ] Encryption keys not committed

### **Before Deployment:**
- [ ] All secrets in environment variables
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Logs don't contain sensitive data

## 📞 Security Contact

If you find any security vulnerabilities, please:
1. **DO NOT** create a public issue
2. Email: [your-email@domain.com]
3. Include detailed description of the vulnerability

## 🔍 Security Audit Commands

```bash
# Check for secrets in code
grep -r "password\|secret\|key\|token" . --exclude-dir=.git --exclude-dir=__pycache__

# Check for environment files
find . -name "*.env*" -type f

# Check git history for sensitive files
git log --all --full-history -- auth-service/key_store/key.txt
git log --all --full-history -- "*.env"
```
