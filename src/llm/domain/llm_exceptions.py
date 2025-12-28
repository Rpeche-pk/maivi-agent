from datetime import datetime
from typing import Optional, Dict, Any


class ServiceLLMError(Exception):
    """El modelo configurado no es válido."""
    pass


class PromptGenerationError(Exception):
    """Error al generar el prompt."""
    pass


class LLMServiceConfigurationError(Exception):
    """Error detallado al configurar el servicio LLM."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        has_tools: bool = False,
        has_structured_output: bool = False,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.timestamp = datetime.now()
        self.model_name = model_name
        self.has_tools = has_tools
        self.has_structured_output = has_structured_output
        self.original_error = original_error
        self.context = context or {}
        
        # Construir mensaje completo
        error_details = [
            f"[LLM Configuration Error] {message}",
            f"Timestamp: {self.timestamp.isoformat()}",
            f"Model: {model_name or 'Unknown'}",
            f"Tools enabled: {has_tools}",
            f"Structured output: {has_structured_output}"
        ]
        
        if original_error:
            error_details.append(f"Original error: {type(original_error).__name__}: {str(original_error)}")
        
        if context:
            error_details.append(f"Context: {context}")
        
        full_message = "\n".join(error_details)
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para logging o serialización."""
        return {
            "error_type": "LLMServiceConfigurationError",
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "model_name": self.model_name,
            "has_tools": self.has_tools,
            "has_structured_output": self.has_structured_output,
            "original_error": str(self.original_error) if self.original_error else None,
            "context": self.context
        }