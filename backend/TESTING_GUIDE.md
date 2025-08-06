# Sentinel-AI 2.0 Testing Guide

This guide will help you test the Sentinel-AI 2.0 project step by step.

## 🚀 Quick Start

### 1. Project Structure Test
First, verify the project structure is correct:

```bash
cd backend
python3 basic_test.py
```

Expected output:
```
🎉 All project tests passed!
✅ Project structure is correct
✅ All required files exist
✅ Python syntax is valid
✅ Import structure is correct
✅ Requirements are properly specified
```

### 2. Demo Overview
Run the demo to see the features:

```bash
python3 demo.py
```

This shows:
- API usage examples
- Curl commands for testing
- Key features overview
- System architecture

## 🧪 Testing Levels

### Level 1: Project Structure (No Dependencies)
```bash
python3 basic_test.py
```
- ✅ All files exist
- ✅ Python syntax is valid
- ✅ Import structure is correct
- ✅ Requirements are specified

### Level 2: Core Logic (With Dependencies)
```bash
# Install dependencies first
pip install -r requirements.txt

# Run core tests
python3 simple_test.py
```
- ✅ Model creation and validation
- ✅ Complexity analysis
- ✅ Prompt optimization
- ✅ Provider selection

### Level 3: Full Application
```bash
# Start the server
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/v1/stats
```

## 📋 Test Checklist

### ✅ Project Setup
- [ ] All required files exist
- [ ] Python syntax is valid
- [ ] Import structure is correct
- [ ] Requirements.txt is complete

### ✅ Core Components
- [ ] Models can be imported
- [ ] Complexity analyzer works
- [ ] Prompt optimizer works
- [ ] Provider registry works
- [ ] Cache manager works
- [ ] Budget controller works

### ✅ API Endpoints
- [ ] Health check endpoint
- [ ] Chat completions endpoint
- [ ] System stats endpoint
- [ ] Budget summary endpoint
- [ ] Cache clear endpoint

### ✅ Integration Tests
- [ ] Full request flow works
- [ ] Caching works correctly
- [ ] Budget control works
- [ ] Provider selection works
- [ ] Error handling works

## 🔧 Manual Testing

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "version": "2.0.0"}`

### 2. Simple Request
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "user_id": "test_user",
    "team_id": "test_team",
    "company_id": "test_company",
    "priority": "normal"
  }'
```
Expected: AI response with metadata

### 3. Complex Request
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Please analyze this code: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)",
    "user_id": "test_user",
    "team_id": "test_team",
    "company_id": "test_company",
    "priority": "high"
  }'
```
Expected: Different provider selection for complex request

### 4. System Statistics
```bash
curl http://localhost:8000/v1/stats
```
Expected: Cache stats, provider metrics, overall performance

### 5. Budget Summary
```bash
curl -X POST "http://localhost:8000/v1/budget/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "test",
    "user_id": "test_user",
    "team_id": "test_team",
    "company_id": "test_company"
  }'
```
Expected: Budget usage at all levels (user, team, company)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're in the `backend` directory
   - Check that all `__init__.py` files exist
   - Verify Python path includes current directory

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Server Won't Start**
   - Check if port 8000 is available
   - Try different port: `uvicorn app.main:app --reload --port 8001`
   - Check for syntax errors in Python files

4. **API Errors**
   - Verify request format matches models
   - Check that all required fields are provided
   - Look at server logs for detailed error messages

### Debug Mode
```bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug

# Check specific component
python3 -c "from app.core.complexity import ComplexityAnalyzer; print('✅ Complexity analyzer imports successfully')"
```

## 📊 Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test with 100 requests
ab -n 100 -c 10 -p test_request.json -T application/json http://localhost:8000/v1/chat/completions/
```

### Memory Testing
```bash
# Monitor memory usage
python3 -m memory_profiler app/main.py
```

## 🔒 Security Testing

### Input Validation
- Test with malformed JSON
- Test with missing required fields
- Test with oversized requests
- Test with special characters

### Rate Limiting
- Test with rapid requests
- Verify rate limiting works
- Check error responses

## 📈 Monitoring

### Key Metrics to Monitor
- Response time (target: < 100ms for cache hits)
- Cache hit rate (target: > 75%)
- Provider success rate (target: > 99%)
- Budget usage (should not exceed limits)
- Error rate (target: < 1%)

### Log Analysis
```bash
# Check for errors
grep "ERROR" logs/app.log

# Check performance
grep "latency" logs/app.log | awk '{print $NF}' | sort -n
```

## 🎯 Success Criteria

### Functional Requirements
- ✅ 75% cost reduction through intelligent routing
- ✅ 99.9% uptime with circuit breakers
- ✅ 3-tier caching system working
- ✅ Hierarchical budget control
- ✅ Prompt optimization (≥50% token reduction)

### Performance Requirements
- ✅ Response time < 100ms for cached requests
- ✅ Cache hit rate > 75%
- ✅ Provider fallback working
- ✅ Budget enforcement working

### Quality Requirements
- ✅ All tests passing
- ✅ No critical errors
- ✅ Proper error handling
- ✅ Comprehensive logging

## 🚀 Next Steps

After successful testing:

1. **Deploy to staging environment**
2. **Set up monitoring and alerting**
3. **Configure production databases**
4. **Set up CI/CD pipeline**
5. **Document API for users**

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Run the basic tests to verify setup
3. Check the API documentation at `/docs`
4. Review the troubleshooting section above

---

**Happy Testing! 🎉**