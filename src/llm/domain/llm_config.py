
from dataclasses import dataclass
from shared.config import settings

@dataclass
class LlmConfig() :
    temperature: float = 0.0
    api_key: str = settings.OPEN_AI_KEY
    model: str