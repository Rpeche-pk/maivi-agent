
from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from llm.domain.llm_entities import LlmConfig

class LlmClient(ABC):
    @abstractmethod
    def llm_client(self,config :LlmConfig) -> Runnable:
        pass