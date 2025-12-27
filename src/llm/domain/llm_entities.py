from dataclasses import dataclass
from typing import List, Any, Optional, Type

from pydantic import BaseModel
from shared.config import settings

@dataclass
class LlmConfig:
    temperature: float = 0.0
    api_key: str = settings.OPEN_AI_KEY
    model: str
    
    
@dataclass
class LLMRequestConfig:
    prompt: str
    tools: Optional[List[Any]] = None
    structured_output: Optional[Type[BaseModel]] = None
    temperature: float = 0.0