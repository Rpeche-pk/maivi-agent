from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from llm.domain.llm_entities import LLMRequestConfig

class LlmService(ABC):
    
    @abstractmethod
    def set_llm_Service(llm_config : LLMRequestConfig) -> Runnable:
        pass