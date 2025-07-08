from typing import Dict, Any, Optional
from ..config import settings # Import the settings instance directly
from ..cultural.thai_cultural_engine import ThaiCulturalEngine # Import the engine

class UniversalDispatcher:
    def __init__(self):
        self.settings = settings # Use the imported settings instance
        self._handlers: Dict[str, Any] = {}

        # Instantiate and register ThaiCulturalEngine
        self.thai_engine = ThaiCulturalEngine()
        self.register_handler("cultural_analysis", self.thai_engine)

    def register_handler(self, handler_type: str, handler: Any) -> None:
        """Register a new handler for a specific type of message."""
        self._handlers[handler_type] = handler

    async def dispatch(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a message to the appropriate handler."""
        handler_type = message.get("type", "default")
        handler = self._handlers.get(handler_type)
        
        if not handler:
            return {
                "status": "error",
                "message": f"No handler found for type: {handler_type}"
            }
        
        try:
            result = await handler.process(message)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            } 