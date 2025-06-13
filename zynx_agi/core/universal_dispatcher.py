from typing import Dict, Any, Optional
from ..config.settings import get_settings

class UniversalDispatcher:
    def __init__(self):
        self.settings = get_settings()
        self._handlers: Dict[str, Any] = {}

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