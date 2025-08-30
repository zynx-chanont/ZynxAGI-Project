# Zynx AGI LLM Gateway

## Overview

The Zynx AGI LLM Gateway is a comprehensive backend service that provides secure, compliant, and intelligent routing of requests to various Large Language Model (LLM) providers. It implements advanced privacy protection, cultural intelligence, and enterprise-grade security features.

## Key Features

### 🔒 **Privacy & Security**
- **PII Detection & Scrubbing**: Automatically detects and redacts personal information (emails, phone numbers, names, IDs)
- **HMAC Pseudonymization**: Generates consistent pseudonyms for audit trails
- **Cross-border Compliance**: Enforces data protection regulations (GDPR, PDPA)
- **Data Retention**: Automatic cleanup of logs after configurable period (default: 90 days)

### 🤖 **Multi-Provider Support**
- **OpenAI Integration**: Full support for GPT models with cultural context
- **Zynx Local**: In-house model support for enhanced privacy
- **Fallback Logic**: Automatic provider switching on failures
- **Cost Estimation**: Real-time pricing calculations for budget management

### 📊 **Monitoring & Analytics**
- **Usage Tracking**: Token consumption, request counts, processing times
- **Error Monitoring**: Provider-specific error tracking and alerting
- **Compliance Reporting**: DPIA requirements and audit logs
- **Cultural Intelligence**: Integration with Thai cultural engine

## API Endpoints

### Main Chat Endpoint
```bash
POST /api/v1/llm/chat
```

**Request Body:**
```json
{
  "message": "Your message here",
  "provider": "openai",           // Optional: "openai", "zynx_local" 
  "model": "gpt-3.5-turbo",      // Optional: specific model
  "temperature": 0.7,             // Optional: 0.0-2.0
  "max_tokens": 150,              // Optional: 1-4000
  "cultural_context": {           // Optional: cultural parameters
    "formality_level": 0.8,
    "politeness_level": 0.9
  },
  "metadata": {}                  // Optional: additional data
}
```

**Response:**
```json
{
  "text": "AI response text",
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "processing_time_ms": 1250.5,
  "cost_estimate": 0.045,
  "compliance": {
    "checks_required": true,
    "dpia_required": false,
    "transfer_allowed": true
  },
  "pii_detected": false,
  "timestamp": "2024-08-30T12:00:00Z"
}
```

### Provider Management
```bash
GET /api/v1/llm/providers
```
Lists available providers and their status.

### Usage Analytics
```bash
GET /api/v1/llm/usage
```
Returns usage statistics and billing information.

### Health Check
```bash
GET /api/v1/llm/health
```
Provider availability and system health status.

## Configuration

Add these settings to your `.env` file:

```env
# LLM Gateway Configuration
ZYNX_LLM_PROVIDER=openai                    # Default provider
ZYNX_LOCAL_API_URL=http://localhost:8001/v1 # Zynx Local model URL
HMAC_PSEUDONYM_KEY=your-secret-key          # PII pseudonymization key
RETENTION_PERIOD_DAYS=90                    # Data retention period
CROSS_BORDER_COMPLIANCE=true               # Enable compliance checks

# Provider API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Security Features

### PII Detection
The gateway automatically detects and redacts:
- Email addresses
- Phone numbers (US, Thai, International)
- Social Security Numbers
- Credit card numbers
- IP addresses
- Formal names and titles
- Thai names and titles

### Compliance Checks
- **GDPR/PDPA Compliance**: Automatic checks for cross-border data transfers
- **DPIA Requirements**: Triggered when PII is detected
- **Audit Logging**: Anonymized request logs for compliance

### Data Protection
- **Request Scrubbing**: PII removed before sending to LLM providers
- **Response Filtering**: PII detection in AI responses
- **Pseudonymization**: HMAC-based consistent pseudonyms for audit trails

## Usage Examples

### Basic Chat Request
```python
import requests

response = requests.post("http://localhost:8000/api/v1/llm/chat", json={
    "message": "Hello, how can you help me today?",
    "temperature": 0.7
})

print(response.json())
```

### Request with Cultural Context
```python
response = requests.post("http://localhost:8000/api/v1/llm/chat", json={
    "message": "สวัสดีครับ ผมต้องการความช่วยเหลือ",
    "cultural_context": {
        "formality_level": 0.9,
        "politeness_level": 0.9
    },
    "provider": "zynx_local"
})
```

### Provider-Specific Request
```python
response = requests.post("http://localhost:8000/api/v1/llm/chat", json={
    "message": "Explain machine learning",
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 300
})
```

## Error Handling

The gateway implements comprehensive error handling:

### Provider Unavailable
```json
{
  "detail": "No LLM providers available"
}
```

### Compliance Violation
```json
{
  "detail": "Cross-border data transfer not allowed: ['PII detected - enhanced protection required']"
}
```

### Rate Limiting
```json
{
  "detail": "LLM generation failed: Rate limit exceeded"
}
```

## Monitoring

### Usage Statistics
Monitor your LLM usage with the `/usage` endpoint:
```json
{
  "usage_stats": {
    "requests_total": 1250,
    "requests_by_provider": {
      "openai": 800,
      "zynx_local": 450
    },
    "errors_by_provider": {
      "openai": 5
    },
    "total_tokens": 50000,
    "total_cost": 75.50
  },
  "retention_period_days": 90,
  "cross_border_compliance": true
}
```

### Health Monitoring
Check system health:
```json
{
  "overall_status": "healthy",
  "providers": {
    "openai": {"available": true, "status": "healthy"},
    "zynx_local": {"available": false, "status": "unavailable"}
  }
}
```

## Fallback Logic

The gateway implements intelligent fallback:

1. **Primary Provider**: Uses configured `ZYNX_LLM_PROVIDER`
2. **Fallback Order**: OpenAI → Zynx Local
3. **Availability Checks**: Real-time provider health monitoring
4. **Error Recovery**: Automatic retry with exponential backoff

## Cultural Intelligence Integration

The gateway integrates with Zynx's Thai Cultural Engine:
- **Automatic Detection**: Thai language and cultural patterns
- **Context Adjustment**: Formality and politeness level adaptation
- **Cultural Validation**: Response appropriateness checking

## Cost Management

### Real-time Cost Estimation
- Token-based pricing calculation
- Per-model cost tracking
- Usage analytics for budget planning

### Billing Integration
- Monthly usage reports
- Provider-specific cost breakdown
- Token consumption analytics

## Best Practices

### Security
- Always use HTTPS in production
- Rotate API keys regularly
- Monitor PII detection logs
- Review compliance reports

### Performance
- Use appropriate temperature settings
- Optimize max_tokens for your use case
- Monitor provider response times
- Implement client-side caching

### Compliance
- Regular DPIA reviews
- Audit log analysis
- Cross-border transfer documentation
- Data retention policy compliance

## Troubleshooting

### Common Issues

**No providers available**
- Check API keys configuration
- Verify network connectivity
- Review provider health status

**PII detection false positives**
- Review PII patterns configuration
- Adjust confidence thresholds
- Whitelist specific patterns if needed

**High response times**
- Check provider status
- Monitor token usage
- Consider model optimization

### Debug Mode
Enable debug logging in production:
```env
DEBUG=true
```

## Contributing

For questions or contributions, please refer to the main Zynx AGI project documentation.

---

*Zynx AGI LLM Gateway - Secure, Intelligent, Culturally Aware AI Processing*