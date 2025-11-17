# ZynxAGI Modules

## Overview

ZynxAGI agents have been rebuilt as **self-contained, modular components** that can be independently instantiated and used without requiring the full ZynxAGI platform. This modular architecture enables:

- **Independent Usage**: Each module can be used standalone
- **Easy Testing**: Modules can be tested in isolation
- **Better Maintainability**: Clear separation of concerns
- **Flexible Integration**: Use only what you need
- **Backward Compatibility**: Original agent classes still available

## Module Structure

Each module follows a consistent structure:

```
zynx_agi/modules/
├── __init__.py              # Module registry
├── zynx/                    # Zynx orchestration module
│   ├── __init__.py
│   ├── agent.py            # Main module implementation
│   ├── config.py           # Configuration settings
│   ├── models.py           # Data models
│   └── utils.py            # Utility functions (optional)
├── deeja/                   # Deeja emotional AI module
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   └── models.py
└── zynx_metadata/          # Zynx-Metadata IP tracking module
    ├── __init__.py
    ├── agent.py
    ├── config.py
    └── models.py
```

## Available Modules

### 1. Zynx Module - Universal AI Orchestration

**Purpose**: Core orchestration, intelligent routing, and AI platform coordination

**Features**:
- Multi-platform AI routing (OpenAI, Anthropic, Google, Local LLM)
- Cultural intelligence detection
- Emotional analysis routing
- IP guardrails and compliance monitoring
- Session management

**Usage**:

```python
from zynx_agi.modules.zynx import ZynxModule, ZynxRequest

# Initialize module
zynx = ZynxModule(config={
    "orchestration_rules": {
        "cultural_context_threshold": 0.7
    }
})

# Initialize and use
await zynx.initialize()

# Process request
request = ZynxRequest(message="Hello, Zynx!")
response = await zynx.process(request)

print(response.message)
print(f"Platform used: {response.platform_used}")
print(f"Processing time: {response.processing_time_ms}ms")

# Get status
status = await zynx.get_status()

# Shutdown when done
await zynx.shutdown()
```

### 2. Deeja Module (ดีจ้า) - Emotional AI & Cultural Intelligence

**Purpose**: Empathetic interactions with Thai cultural specialization

**Features**:
- Cultural analysis (Thai language detection, formality scoring)
- Emotional intelligence (sentiment analysis, emotion detection)
- Empathy scoring and calibration
- Thai cultural marker detection (kreng_jai, sanuk, mai_pen_rai, etc.)
- Ethical reasoning framework
- Culturally appropriate response generation

**Usage**:

```python
from zynx_agi.modules.deeja import DeejaModule, DeejaRequest

# Initialize module
deeja = DeejaModule(config={
    "cultural_sensitivity_weight": 0.3,
    "thai_context_boost": 0.3
})

await deeja.initialize()

# Process Thai message
request = DeejaRequest(message="สวัสดีครับ ยินดีที่ได้รู้จักครับ")
response = await deeja.process(request)

print(response.message)
print(f"Language: {response.cultural_analysis.language_detected}")
print(f"Formality: {response.cultural_analysis.formality_level}")
print(f"Empathy score: {response.empathy_score}")
print(f"Thai markers: {response.cultural_analysis.thai_markers}")

# Process emotional content
request = DeejaRequest(message="I'm feeling sad today")
response = await deeja.process(request)

print(f"Sentiment: {response.emotional_analysis.sentiment}")
print(f"Emotions: {response.emotional_analysis.detected_emotions}")
print(f"Support needed: {response.emotional_analysis.emotional_support_needed}")

await deeja.shutdown()
```

### 3. Zynx-Metadata Module - Autonomous IP Tracking

**Purpose**: Intellectual property tracking and attribution management

**Features**:
- Intent detection (discover, invent, develop, create)
- Automatic attribution and metadata generation
- Multi-format logging (JSON, Markdown, PDF)
- SHA-256 hashing and verification
- Defensive publication generation
- ZPDL v1.0 license embedding

**Usage**:

```python
from zynx_agi.modules.zynx_metadata import ZynxMetadataModule
from pathlib import Path

# Initialize module
metadata = ZynxMetadataModule(
    storage_path=Path("./logs"),
    config={
        "auto_detect_intent": True,
        "generate_json": True,
        "generate_markdown": True
    }
)

await metadata.initialize()

# Observe agent interaction
observation = await metadata.observe_interaction(
    agent_name="deeja",
    user_input="I discovered a new algorithm for Thai NLP",
    agent_response="That's an interesting discovery!"
)

if observation.tracked:
    print(f"Intent detected: {observation.intent_detected}")
    print(f"UUID: {observation.metadata.uuid}")
    print(f"SHA-256: {observation.metadata.sha256}")
    print(f"Files: {observation.storage_paths}")
    
    # Generate defensive publication
    pub_path = await metadata.generate_defensive_publication(
        observation.metadata.uuid
    )
    print(f"Defensive publication: {pub_path}")

# List active sessions
sessions = await metadata.list_active_sessions()
print(f"Active sessions: {len(sessions)}")

await metadata.shutdown()
```

## Configuration

Each module can be configured through its config class or dictionary:

### Zynx Configuration

```python
from zynx_agi.modules.zynx import ZynxConfig

config = ZynxConfig(
    module_id="zynx_main",
    ai_platforms={
        "openai": {"status": "available", "priority": 1},
        "anthropic": {"status": "available", "priority": 2}
    },
    orchestration_rules={
        "cultural_context_threshold": 0.7,
        "emotional_intelligence_required": True,
        "ip_guardrails_enabled": True,
        "compliance_monitoring": True
    },
    log_level="INFO"
)

zynx = ZynxModule(config=config)
```

### Deeja Configuration

```python
from zynx_agi.modules.deeja import DeejaConfig

config = DeejaConfig(
    module_id="deeja",
    emotional_awareness_weight=0.3,
    cultural_sensitivity_weight=0.3,
    thai_cultural_weight=0.2,
    baseline_empathy_score=0.5,
    thai_context_boost=0.3,
    log_level="INFO"
)

deeja = DeejaModule(config=config)
```

### Zynx-Metadata Configuration

```python
from zynx_agi.modules.zynx_metadata import ZynxMetadataConfig
from pathlib import Path

config = ZynxMetadataConfig(
    module_id="zynx_metadata",
    storage_path=Path("./zynx_logs"),
    generate_json=True,
    generate_markdown=True,
    generate_pdf=False,
    auto_detect_intent=True,
    auto_embed_attribution=True,
    log_level="INFO"
)

metadata = ZynxMetadataModule(config=config)
```

## Module Interoperability

All three modules can work together seamlessly:

```python
from zynx_agi.modules import ZynxModule, DeejaModule, ZynxMetadataModule

# Initialize all modules
zynx = ZynxModule()
deeja = DeejaModule()
metadata = ZynxMetadataModule()

await zynx.initialize()
await deeja.initialize()
await metadata.initialize()

# Process through Zynx orchestration
zynx_response = await zynx.process(
    ZynxRequest(message="สวัสดีครับ")
)

# Get cultural analysis from Deeja
deeja_response = await deeja.process(
    DeejaRequest(message="สวัสดีครับ")
)

# Track the interaction
observation = await metadata.observe_interaction(
    agent_name="orchestration",
    user_input="สวัสดีครับ",
    agent_response=deeja_response.message
)

# Cleanup
await zynx.shutdown()
await deeja.shutdown()
await metadata.shutdown()
```

## Backward Compatibility

The original agent classes remain available for backward compatibility:

```python
# Old way (still works)
from zynx_agi.agents import ZynxMainAgent, DeejaAgent, ZynxMetadataAgent

zynx = ZynxMainAgent()
deeja = DeejaAgent()
metadata = ZynxMetadataAgent()

# New way (recommended for new code)
from zynx_agi.modules import ZynxModule, DeejaModule, ZynxMetadataModule

zynx = ZynxModule()
deeja = DeejaModule()
metadata = ZynxMetadataModule()
```

## Testing

Each module has comprehensive test coverage:

```bash
# Run all tests
pytest tests/ -v

# Run module-specific tests
pytest tests/test_modules.py -v

# Run specific module tests
pytest tests/test_modules.py::TestZynxModule -v
pytest tests/test_modules.py::TestDeejaModule -v
pytest tests/test_modules.py::TestZynxMetadataModule -v
```

## Benefits of Modular Architecture

1. **Independence**: Each module can be used standalone
2. **Testability**: Easier to test in isolation
3. **Maintainability**: Clear separation of concerns
4. **Flexibility**: Use only what you need
5. **Scalability**: Modules can be deployed independently
6. **Reusability**: Modules can be reused across projects
7. **Documentation**: Better organized documentation per module

## Future Enhancements

- **Module Registry**: Central registry for module discovery
- **Module Versioning**: Version management for modules
- **Module Dependencies**: Explicit dependency management
- **Module Packaging**: Standalone package distribution
- **Module Marketplace**: Share and discover community modules

## Contributing

When adding new functionality:

1. Keep module implementations self-contained
2. Maintain consistent structure across modules
3. Add comprehensive tests for new functionality
4. Update module documentation
5. Ensure backward compatibility

## License

All modules are licensed under ZPDL v1.0 © Chanont Waenkaew

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0  
**Author**: Chanont Waenkaew (Zynx)
