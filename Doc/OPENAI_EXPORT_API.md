# OpenAI Export API Documentation

## Overview

The OpenAI Export API allows you to export all prompts, configurations, and agent definitions from your ZynxAGI OpenAI integration. This is useful for:

- **Backup**: Create backups of your AI configurations
- **Migration**: Move configurations between environments
- **Version Control**: Track changes to prompts and configurations
- **Documentation**: Document your AI setup
- **Compliance**: Maintain records for ZPDL/PDPA compliance

## Base URL

All API endpoints are prefixed with:
```
http://localhost:8000/api/v1/export
```

## API Endpoints

### 1. Export Status

**Endpoint:** `GET /api/v1/export/status`

**Description:** Get the status of the export system and available capabilities.

**Response:**
```json
{
  "success": true,
  "export_system": "operational",
  "available_export_types": ["all", "prompts", "configs", "agents"],
  "supported_formats": ["json"],
  "storage_backend": "memory",
  "version": "1.0.0"
}
```

### 2. Export All Assets

**Endpoint:** `POST /api/v1/export/openai`

**Description:** Export all OpenAI assets including prompts, configurations, and agent definitions.

**Request Body:**
```json
{
  "export_type": "all",
  "include_agents": true,
  "agent_ids": ["deeja", "zynx_main"]  // Optional
}
```

**Parameters:**
- `export_type` (string, required): Type of export - `"all"`, `"prompts"`, `"configs"`, or `"agents"`
- `include_agents` (boolean): Whether to include agent definitions (default: true)
- `agent_ids` (array of strings, optional): Specific agent IDs to export. If omitted, all agents are exported.

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_assets_export_20251117_122631_3af4b9bc",
  "exported_at": "2025-11-17T12:26:31.622763",
  "summary": {
    "system_prompts_count": 3,
    "model_configs_count": 3,
    "agent_definitions_count": 3,
    "platform_settings_exported": true
  },
  "download_url": "/api/v1/export/download/openai_assets_export_20251117_122631_3af4b9bc"
}
```

### 3. Export Prompts Only

**Endpoint:** `GET /api/v1/export/openai/prompts`

**Description:** Export only system prompts used by agents and configurations.

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_prompts_export_20251117_122614_24455619",
  "exported_at": "2025-11-17T12:26:14.834554",
  "prompts_count": 3,
  "download_url": "/api/v1/export/download/openai_prompts_export_20251117_122614_24455619"
}
```

**Exported Prompts Include:**
- Cultural awareness prompt (English/Thai support)
- Thai cultural prompt with kreng_jai, sanuk, mai_pen_rai elements
- Empathy-first philosophy prompt
- Agent-specific prompts from Deeja, Zynx Main, Zynx Metadata

### 4. Export Configurations Only

**Endpoint:** `GET /api/v1/export/openai/configs`

**Description:** Export only OpenAI model configurations.

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_configs_export_20251117_122622_4d63ee36",
  "exported_at": "2025-11-17T12:26:22.761056",
  "configs_count": 3,
  "download_url": "/api/v1/export/download/openai_configs_export_20251117_122622_4d63ee36"
}
```

**Exported Configurations Include:**
- **Default OpenAI Config**: gpt-4, temperature 0.7, 1000 max tokens
- **Cultural Config**: gpt-4, temperature 0.8, 1500 max tokens, cultural weight 0.8
- **Empathy Config**: gpt-4, temperature 0.9, 2000 max tokens, empathy threshold 0.7

### 5. Export Agents Only

**Endpoint:** `GET /api/v1/export/openai/agents`

**Description:** Export only agent definitions.

**Query Parameters:**
- `agent_ids` (string, optional): Comma-separated list of agent IDs to export

**Example:**
```
GET /api/v1/export/openai/agents?agent_ids=deeja,zynx_main
```

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_agents_export_20251117_122635_abc123",
  "exported_at": "2025-11-17T12:26:35.123456",
  "agents_count": 2,
  "download_url": "/api/v1/export/download/openai_agents_export_20251117_122635_abc123"
}
```

**Exported Agent Data Includes:**
- Agent ID and type
- Capabilities (chat, cultural_analysis, emotional_intelligence, etc.)
- Active status and metrics
- Configuration settings
- Empathy models and cultural contexts
- Ethical frameworks

### 6. Download Export

**Endpoint:** `GET /api/v1/export/download/{artifact_id}`

**Description:** Download the exported data in JSON format.

**Parameters:**
- `artifact_id` (string, path parameter): The artifact ID from the export response

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_configs_export_20251117_122622_4d63ee36",
  "data": {
    "export_metadata": {
      "exported_at": "2025-11-17T12:26:22.761056",
      "export_type": "configs_only",
      "source_platform": "openai",
      "version": "1.0.0"
    },
    "model_configurations": {
      "default_openai_config": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "configuration_type": "default",
        "purpose": "Default OpenAI API configuration",
        "version": "1.0.0"
      }
      // ... more configurations
    }
  },
  "metadata": {
    "type": "openai_configs_export",
    "created_at": "2025-11-17T12:26:22.761182",
    "content_type": "application/json",
    "tags": ["openai", "configs", "export"],
    "zpdl_compliance": true,
    "pdpa_compliant": true
  }
}
```

### 7. Import Assets

**Endpoint:** `POST /api/v1/export/import/{artifact_id}`

**Description:** Import previously exported OpenAI assets.

**Parameters:**
- `artifact_id` (string, path parameter): The artifact ID to import

**Response:**
```json
{
  "success": true,
  "artifact_id": "openai_assets_export_20251117_122631_3af4b9bc",
  "imported_at": "2025-11-17T12:30:00.123456",
  "original_export_date": "2025-11-17T12:26:31.622763",
  "summary": {
    "prompts_imported": 3,
    "configs_imported": 3,
    "agents_imported": 3
  }
}
```

### 8. List All Exports

**Endpoint:** `GET /api/v1/export/list`

**Description:** List all available export artifacts.

**Response:**
```json
{
  "success": true,
  "total_exports": 5,
  "exports": [
    {
      "artifact_id": "openai_assets_export_20251117_122631_3af4b9bc",
      "type": "openai_assets_export",
      "created_at": "2025-11-17T12:26:31.622763",
      "size": 12345,
      "tags": ["openai", "export", "backup"]
    }
    // ... more exports
  ]
}
```

## Export Data Structure

### System Prompts Export Structure

```json
{
  "export_metadata": {
    "exported_at": "2025-11-17T12:26:14.834554",
    "export_type": "prompts_only",
    "source_platform": "openai",
    "version": "1.0.0"
  },
  "system_prompts": {
    "common": {
      "cultural_awareness_prompt": {
        "content": "You are a culturally aware AI assistant...",
        "language_support": ["en", "th"],
        "purpose": "Base cultural awareness prompt",
        "version": "1.0.0"
      },
      "thai_cultural_prompt": {
        "content": "คุณเป็นผู้ช่วย AI ที่เข้าใจวัฒนธรรมไทย...",
        "language_support": ["th"],
        "purpose": "Thai cultural awareness prompt",
        "cultural_elements": ["kreng_jai", "sanuk", "mai_pen_rai"],
        "version": "1.0.0"
      }
    },
    "deeja": {
      // Agent-specific prompts
    }
  }
}
```

### Model Configurations Export Structure

```json
{
  "export_metadata": {
    "exported_at": "2025-11-17T12:26:22.761056",
    "export_type": "configs_only",
    "source_platform": "openai",
    "version": "1.0.0"
  },
  "model_configurations": {
    "default_openai_config": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1000,
      "top_p": 1.0,
      "frequency_penalty": 0.0,
      "presence_penalty": 0.0,
      "configuration_type": "default",
      "purpose": "Default OpenAI API configuration",
      "version": "1.0.0"
    },
    "cultural_config": {
      "model": "gpt-4",
      "temperature": 0.8,
      "max_tokens": 1500,
      "top_p": 0.95,
      "configuration_type": "cultural_aware",
      "purpose": "Configuration for culturally aware responses",
      "cultural_weight": 0.8,
      "version": "1.0.0"
    }
  }
}
```

### Agent Definitions Export Structure

```json
{
  "export_metadata": {
    "exported_at": "2025-11-17T12:26:35.123456",
    "export_type": "agents_only",
    "source_platform": "openai",
    "version": "1.0.0"
  },
  "agent_definitions": {
    "deeja": {
      "agent_id": "deeja",
      "agent_type": "DeejaAgent",
      "capabilities": [
        "cultural_analysis",
        "emotional_intelligence",
        "empathy_scoring",
        "translation",
        "chat"
      ],
      "active": true,
      "configuration": {},
      "metrics": {
        "requests_processed": 0,
        "total_processing_time": 0.0,
        "errors": 0
      },
      "empathy_model": {
        "emotional_awareness_weight": 0.3,
        "cultural_sensitivity_weight": 0.3,
        "thai_cultural_weight": 0.2
      },
      "cultural_contexts": {
        "formal_business": {
          "formality_level": 0.9,
          "required_markers": ["kreng_jai", "bun_khun"]
        }
      },
      "ethical_framework": {
        "principles": [
          "respect_for_persons",
          "beneficence",
          "cultural_sensitivity"
        ],
        "thai_values": [
          "kreng_jai_respect",
          "sanuk_positivity"
        ]
      }
    }
  }
}
```

## Usage Examples

### cURL Examples

#### Export all assets:
```bash
curl -X POST "http://localhost:8000/api/v1/export/openai" \
  -H "Content-Type: application/json" \
  -d '{"export_type": "all", "include_agents": true}'
```

#### Export only prompts:
```bash
curl -X GET "http://localhost:8000/api/v1/export/openai/prompts"
```

#### Download an export:
```bash
curl -X GET "http://localhost:8000/api/v1/export/download/{artifact_id}" \
  > export.json
```

### Python Example

```python
import requests

# Export all assets
response = requests.post(
    "http://localhost:8000/api/v1/export/openai",
    json={
        "export_type": "all",
        "include_agents": True,
        "agent_ids": ["deeja", "zynx_main"]
    }
)

result = response.json()
artifact_id = result["artifact_id"]

# Download the export
download_response = requests.get(
    f"http://localhost:8000/api/v1/export/download/{artifact_id}"
)

export_data = download_response.json()
print(f"Exported {len(export_data['data']['agent_definitions'])} agents")

# Save to file
import json
with open("openai_export.json", "w") as f:
    json.dump(export_data, f, indent=2, ensure_ascii=False)
```

### JavaScript/TypeScript Example

```typescript
// Export configurations
const exportConfigs = async () => {
  const response = await fetch(
    "http://localhost:8000/api/v1/export/openai/configs"
  );
  const result = await response.json();
  
  console.log(`Exported ${result.configs_count} configurations`);
  console.log(`Download URL: ${result.download_url}`);
  
  return result.artifact_id;
};

// Download and save
const downloadExport = async (artifactId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/export/download/${artifactId}`
  );
  const exportData = await response.json();
  
  // Save to localStorage or file
  localStorage.setItem('openai_export', JSON.stringify(exportData));
};

// Usage
const artifactId = await exportConfigs();
await downloadExport(artifactId);
```

## Error Responses

All endpoints return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

## Compliance

All exports include compliance metadata:

- **ZPDL v1.0**: Zynx Privacy Definition Language compliance
- **PDPA**: Personal Data Protection Act compliance
- **Data Privacy**: Enabled by default

Export artifacts are stored with integrity hashes (SHA-256) and can be encrypted if encryption keys are configured.

## Best Practices

1. **Regular Backups**: Export your configurations regularly to maintain backups
2. **Version Control**: Track changes by comparing export timestamps
3. **Testing**: Test imports in a development environment before production
4. **Storage**: Store export artifacts securely with appropriate access controls
5. **Documentation**: Use exports to document your AI setup and configuration changes

## Migration Workflow

1. **Export from Source**:
   ```bash
   curl -X POST "http://source.example.com/api/v1/export/openai" \
     -d '{"export_type": "all"}' > source_export.json
   ```

2. **Review Export**:
   - Verify all required prompts, configs, and agents are included
   - Check compliance metadata

3. **Import to Target**:
   ```bash
   # Upload artifact first (implementation-specific)
   curl -X POST "http://target.example.com/api/v1/export/import/{artifact_id}"
   ```

4. **Verify Import**:
   - Test agents are working correctly
   - Verify configurations are applied
   - Check prompts are loaded

## Support

For issues or questions about the Export API:
- Check the API documentation at `/docs`
- Review test files in `tests/test_openai_export.py`
- Check implementation in `zynx_agi/storage/openai_exporter.py`
