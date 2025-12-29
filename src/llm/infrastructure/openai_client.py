
from langchain_openai import ChatOpenAI
from llm.domain.llm_client import LlmClient
from llm.domain.llm_entities import LlmConfig
from shared.init_logger import init_logger

class OpenAIClient(LlmClient):
    
    
    def __init__(self):
        self.log = init_logger(self.__class__.__name__)
        

    def llm_client(self,config :LlmConfig) -> ChatOpenAI:
        try:
            
            self.log.info(f"[INFRASTRUCTURE] Creando el cliente ai con modelo {config.model}")
            return ChatOpenAI(
                name=config.name_agent,
                api_key= config.api_key,
                model= config.model,
                temperature= config.temperature,
            )
            
        except Exception as e:
            self.log.error(f"[ERROR] details: {e}")
            raise