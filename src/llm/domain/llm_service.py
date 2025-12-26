from abc import ABC, abstractmethod


class LlmService(ABC):
    
    @abstractmethod
    def set_llm_Service():
        pass