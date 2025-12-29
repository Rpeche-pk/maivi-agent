from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Optional, Type

from pydantic import BaseModel
from shared.config import settings

class UserInputType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"


@dataclass
class LlmConfig:
    model: str
    name_agent: str = settings.NAME_AGENT
    temperature: float = 0.0
    api_key: str = settings.OPEN_AI_KEY
    
    
@dataclass
class LLMRequestConfig:
    input_type: UserInputType
    prompt: str
    tools: Optional[List[Any]] = None
    structured_output: Optional[Type[BaseModel]] = None
    temperature: float = 0.0