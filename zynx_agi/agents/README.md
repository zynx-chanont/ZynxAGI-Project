# ZynxAGI Agents Framework

This directory contains the AI agents framework for the ZynxAGI ecosystem. Each agent is a specialized component designed for specific tasks and they all collaborate through the Model Context Protocol (MCP).

## Architecture

### Base Components

- **BaseAgent**: Abstract base class that all agents inherit from
- **AgentRegistry**: Central registry for managing agent lifecycle and discovery
- **AgentManifest**: Configuration structure defining agent capabilities and metadata

### Available Agents

#### CodeD Agent (`/coded`)
**Status**: 🟢 Live

A specialized coding assistant that provides:

- **Code Generation**: Generate code from natural language descriptions
- **Debugging**: Analyze errors and provide solutions
- **Code Review**: Review code quality and best practices
- **Documentation**: Generate docstrings and technical documentation
- **Optimization**: Suggest performance improvements
- **Security Analysis**: Identify potential security issues

**Supported Languages**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, Ruby, Swift, Kotlin, Scala, HTML, CSS, SQL, Bash, YAML, JSON, XML

**Usage Examples**:
```
/coded generate a Python function to calculate fibonacci numbers
/coded debug this error: NameError: 'x' is not defined
/coded review my code: [paste your code]
/coded document this function: [paste your function]
/coded optimize this algorithm for better performance
```

## API Endpoints

### Agent Management
- `GET /api/v1/agents` - List all registered agents
- `GET /api/v1/agents/{agent_id}` - Get specific agent information
- `POST /api/v1/agents/{agent_id}/process` - Process request through specific agent

### Chat Integration
- `POST /api/v1/chat/message` - Process messages with MCP command support

## MCP (Model Context Protocol)

Agents are accessed through MCP commands in the format:
```
/{agent_command} {request_text}
```

Example:
```
/coded generate a hello world function
```

## Development

### Creating a New Agent

1. Create a new agent class inheriting from `BaseAgent`
2. Implement required abstract methods:
   - `process_request()` - Main request processing logic
   - `get_capabilities()` - List of agent capabilities

3. Register the agent in `main.py`:
```python
from .agents.my_agent import MyAgent

def initialize_agents():
    my_agent = MyAgent()
    manifest = AgentManifest({
        "name": "MyAgent",
        "version": "1.0.0",
        "description": "Description of what this agent does",
        "capabilities": my_agent.get_capabilities(),
        "mcp_command": "/myagent"
    })
    registry.register_agent("myagent", manifest, my_agent)
```

### Testing

Run agent tests with:
```bash
python -m pytest tests/test_*_agent.py -v
```

## Cultural Intelligence Integration

All agents integrate with ZynxAGI's cultural intelligence system, providing culturally-aware responses that adapt to Thai and international communication styles while maintaining technical accuracy.

## Future Agents

The framework is designed to support additional agents as defined in the main AGENTS.md:

- **Verifier**: Fact-checking and validation agent
- **Dispatcher**: Central routing and orchestration (partially implemented)
- Additional specialized agents as needed

## Contributing

When adding new agents:
1. Follow the established patterns in CodeD agent
2. Include comprehensive tests
3. Update documentation
4. Ensure cultural intelligence integration
5. Add proper error handling and logging