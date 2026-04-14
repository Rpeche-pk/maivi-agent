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
    """Para analizar una imagen debes elegir el type (IMAGE)y llenar el campo image_base64"""
    input_type: UserInputType
    prompt: str
    image_base64: Optional[str] = None
    tools: Optional[List[Any]] = None
    structured_output: Optional[Type[BaseModel]] = None
    temperature: float = 0.0
    
class ImagePrompt:
    chat_prompt: str