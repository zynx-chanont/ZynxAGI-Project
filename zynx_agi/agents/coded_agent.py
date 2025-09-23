"""
CodeD Agent - Specialized coding assistant for ZynxAGI
Provides code generation, analysis, debugging, and optimization capabilities
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodeDAgent(BaseAgent):
    """
    CodeD Agent - Specialized coding assistant for the ZynxAGI ecosystem
    Handles code generation, analysis, debugging, and optimization tasks
    """
    
    def __init__(self):
        super().__init__(
            agent_id="coded",
            name="CodeD",
            version="1.0.0"
        )
        self.mcp_command = "/coded"
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "cpp", "c",
            "go", "rust", "php", "ruby", "swift", "kotlin", "scala",
            "html", "css", "sql", "bash", "yaml", "json", "xml"
        ]
        self.logger.info("CodeD Agent initialized")
    
    def get_capabilities(self) -> List[str]:
        """Return list of CodeD capabilities"""
        return [
            "code_generation",
            "error_analysis", 
            "debugging_suggestions",
            "code_optimization",
            "documentation_generation",
            "code_review",
            "refactoring_suggestions",
            "security_analysis",
            "performance_analysis",
            "unit_test_generation"
        ]
    
    async def process_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process coding-related requests"""
        try:
            context = context or {}
            
            # Detect the type of coding request
            request_type = self._detect_request_type(message)
            
            # Process based on request type
            if request_type == "code_generation":
                return await self._generate_code(message, context)
            elif request_type == "debug_analysis":
                return await self._analyze_debug(message, context)
            elif request_type == "code_review":
                return await self._review_code(message, context)
            elif request_type == "documentation":
                return await self._generate_documentation(message, context)
            elif request_type == "optimization":
                return await self._optimize_code(message, context)
            else:
                return await self._general_coding_help(message, context)
                
        except Exception as e:
            self.logger.error(f"Error processing CodeD request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Sorry, I encountered an error while processing your coding request.",
                "agent": "coded",
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_request_type(self, message: str) -> str:
        """Detect the type of coding request from the message"""
        message_lower = message.lower()
        
        # Optimization patterns
        if any(phrase in message_lower for phrase in [
            "optimize", "improve", "faster", "performance", "efficient"
        ]):
            return "optimization"
        
        # Code generation patterns
        if any(phrase in message_lower for phrase in [
            "write", "create", "generate", "build", "make", "code for"
        ]):
            return "code_generation"
        
        # Debug/error analysis patterns  
        if any(phrase in message_lower for phrase in [
            "error", "bug", "debug", "fix", "broken", "not working", "exception"
        ]):
            return "debug_analysis"
        
        # Code review patterns
        if any(phrase in message_lower for phrase in [
            "review", "check", "analyze", "look at", "examine"
        ]):
            return "code_review"
        
        # Documentation patterns
        if any(phrase in message_lower for phrase in [
            "document", "docstring", "comment", "explain", "description"
        ]):
            return "documentation"
        
        return "general"
    
    def _detect_language(self, code_text: str) -> str:
        """Detect programming language from code snippet"""
        # Simple language detection based on common patterns
        if "def " in code_text and ":" in code_text:
            return "python"
        elif "function" in code_text and "{" in code_text:
            return "javascript"
        elif "public class" in code_text or "private" in code_text:
            return "java"
        elif "#include" in code_text:
            return "cpp"
        elif "<?php" in code_text:
            return "php"
        elif "fn " in code_text and "let " in code_text:
            return "rust"
        elif "package main" in code_text:
            return "go"
        else:
            return "unknown"
    
    async def _generate_code(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on natural language description"""
        # Extract language preference if specified
        language = context.get("language", "python")
        
        # Simple code generation based on common patterns
        code_examples = {
            "hello world": {
                "python": 'print("Hello, World!")',
                "javascript": 'console.log("Hello, World!");',
                "java": 'System.out.println("Hello, World!");'
            },
            "api endpoint": {
                "python": '''from fastapi import FastAPI

app = FastAPI()

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from API"}''',
                "javascript": '''const express = require('express');
const app = express();

app.get('/api/data', (req, res) => {
    res.json({ message: 'Hello from API' });
});'''
            },
            "database connection": {
                "python": '''import sqlite3

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

def get_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()''',
                "javascript": '''const mysql = require('mysql2');

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'your_username',
    password: 'your_password',
    database: 'your_database'
});

connection.connect();'''
            }
        }
        
        # Find matching code example
        message_lower = message.lower()
        generated_code = None
        explanation = None
        
        for pattern, examples in code_examples.items():
            if pattern in message_lower:
                generated_code = examples.get(language, examples.get("python"))
                explanation = f"Generated {language} code for {pattern}"
                break
        
        if not generated_code:
            # Provide general template based on detected intent
            if "function" in message_lower:
                if language == "python":
                    generated_code = '''def my_function(param1, param2):
    """
    Description of what this function does
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    """
    # Implementation here
    result = param1 + param2
    return result'''
                else:
                    generated_code = '''function myFunction(param1, param2) {
    // Description of what this function does
    // Implementation here
    return param1 + param2;
}'''
                explanation = f"Generated a basic {language} function template"
        
        if not generated_code:
            generated_code = f"# I need more specific details to generate {language} code for your request"
            explanation = "Please provide more specific requirements for code generation"
        
        return {
            "success": True,
            "response_type": "code_generation",
            "generated_code": generated_code,
            "language": language,
            "explanation": explanation,
            "suggestions": [
                "Add error handling",
                "Include input validation", 
                "Add unit tests",
                "Consider performance optimization"
            ],
            "agent": "coded",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_debug(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze debugging requests and provide suggestions"""
        
        # Extract code from message if present
        code_match = re.search(r'```(\w+)?\n(.*?)\n```', message, re.DOTALL)
        code_snippet = code_match.group(2) if code_match else None
        language = code_match.group(1) if code_match else self._detect_language(message)
        
        analysis = []
        suggestions = []
        
        if code_snippet:
            # Analyze common issues
            if "undefined" in message.lower() or "nameerror" in message.lower():
                analysis.append("Variable/function name error detected")
                suggestions.extend([
                    "Check variable names for typos",
                    "Ensure variables are defined before use",
                    "Check import statements"
                ])
            
            if "syntax" in message.lower():
                analysis.append("Syntax error detected")
                suggestions.extend([
                    "Check for missing brackets, parentheses, or quotes",
                    "Verify proper indentation",
                    "Check for missing semicolons (if required by language)"
                ])
            
            if "index" in message.lower() or "bounds" in message.lower():
                analysis.append("Array/list index error detected")
                suggestions.extend([
                    "Check array/list length before accessing elements",
                    "Verify index values are within valid range",
                    "Add boundary checks"
                ])
        
        if not analysis:
            analysis = ["General debugging assistance"]
            suggestions = [
                "Add print/log statements to track variable values",
                "Use debugger or IDE debugging tools",
                "Break down complex operations into smaller steps",
                "Check documentation for correct API usage"
            ]
        
        return {
            "success": True,
            "response_type": "debug_analysis",
            "analysis": analysis,
            "suggestions": suggestions,
            "language": language,
            "code_snippet": code_snippet,
            "agent": "coded",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _review_code(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide code review feedback"""
        
        code_match = re.search(r'```(\w+)?\n(.*?)\n```', message, re.DOTALL)
        code_snippet = code_match.group(2) if code_match else None
        language = code_match.group(1) if code_match else "unknown"
        
        if not code_snippet:
            return {
                "success": False,
                "message": "Please provide code snippet for review using ```language code``` format",
                "agent": "coded",
                "timestamp": datetime.now().isoformat()
            }
        
        feedback = []
        
        # Basic code quality checks
        if len(code_snippet.split('\n')) > 20:
            feedback.append("Consider breaking large functions into smaller, more focused functions")
        
        if not any(line.strip().startswith('#') or line.strip().startswith('//') for line in code_snippet.split('\n')):
            feedback.append("Add comments to explain complex logic")
        
        if language == "python":
            if "def " in code_snippet and '"""' not in code_snippet:
                feedback.append("Add docstrings to functions for better documentation")
        
        # Security considerations
        if "eval(" in code_snippet:
            feedback.append("⚠️ Security: Avoid using eval() as it can execute arbitrary code")
        
        if "sql" in code_snippet.lower() and ("%" in code_snippet or "+" in code_snippet):
            feedback.append("⚠️ Security: Use parameterized queries to prevent SQL injection")
        
        if not feedback:
            feedback = ["Code looks good! Consider adding unit tests and error handling."]
        
        return {
            "success": True,
            "response_type": "code_review",
            "feedback": feedback,
            "language": language,
            "code_snippet": code_snippet,
            "rating": "good" if len(feedback) <= 2 else "needs_improvement",
            "agent": "coded",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_documentation(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for code"""
        
        code_match = re.search(r'```(\w+)?\n(.*?)\n```', message, re.DOTALL)
        code_snippet = code_match.group(2) if code_match else None
        language = code_match.group(1) if code_match else "python"
        
        if not code_snippet:
            return {
                "success": False,
                "message": "Please provide code snippet for documentation generation",
                "agent": "coded",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate basic documentation
        if language == "python":
            documentation = '''"""
Function/Class Documentation

Description:
    This function/class performs [describe main functionality]

Parameters:
    param1 (type): Description of parameter 1
    param2 (type): Description of parameter 2

Returns:
    return_type: Description of return value

Example:
    >>> result = function_name(arg1, arg2)
    >>> print(result)
    
Raises:
    ExceptionType: Description of when this exception is raised
"""'''
        else:
            documentation = '''/**
 * Function/Class Documentation
 * 
 * @description This function/class performs [describe main functionality]
 * @param {type} param1 - Description of parameter 1  
 * @param {type} param2 - Description of parameter 2
 * @returns {type} Description of return value
 * @example
 * const result = functionName(arg1, arg2);
 * console.log(result);
 */'''
        
        return {
            "success": True,
            "response_type": "documentation",
            "documentation": documentation,
            "language": language,
            "suggestions": [
                "Customize parameter types and descriptions",
                "Add usage examples", 
                "Include error handling documentation",
                "Consider adding version information"
            ],
            "agent": "coded",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _optimize_code(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide code optimization suggestions"""
        
        optimizations = [
            "Use list comprehensions instead of loops (Python)",
            "Cache frequently used calculations",
            "Use appropriate data structures (e.g., sets for membership testing)",
            "Minimize database queries by batching operations",
            "Use async/await for I/O operations",
            "Implement proper indexing for database tables",
            "Use CDN for static assets",
            "Implement caching strategies",
            "Profile your code to identify bottlenecks"
        ]
        
        return {
            "success": True,
            "response_type": "optimization",
            "optimizations": optimizations[:5],  # Return top 5 suggestions
            "categories": ["performance", "memory", "readability", "maintainability"],
            "agent": "coded", 
            "timestamp": datetime.now().isoformat()
        }
    
    async def _general_coding_help(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general coding assistance"""
        
        help_message = """I'm CodeD, your coding assistant! I can help you with:

🔧 **Code Generation**: Write code from natural language descriptions
🐛 **Debugging**: Analyze errors and provide solutions  
📝 **Code Review**: Review your code for quality and best practices
📚 **Documentation**: Generate docstrings and comments
⚡ **Optimization**: Suggest performance improvements

**How to use me:**
- `/coded generate a Python function to calculate fibonacci`
- `/coded debug this error: NameError: 'x' is not defined`  
- `/coded review my code: [paste your code]`
- `/coded document this function: [paste your function]`
- `/coded optimize this algorithm: [paste your code]`

**Supported languages:** Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, Ruby, and more!

What would you like help with today?"""

        return {
            "success": True,
            "response_type": "general_help",
            "message": help_message,
            "capabilities": self.get_capabilities(),
            "supported_languages": self.supported_languages[:10],  # Show first 10
            "agent": "coded",
            "timestamp": datetime.now().isoformat()
        }