
from langchain_openai import ChatOpenAI
from llm.domain.llm_client import LlmClient
from llm.domain.llm_entities import LlmConfig
from shared.init_logger import init_logger

class OpenAIClient(LlmClient):
    
    
    def __init__(self):
        self.log = init_logger("open_ai_client")
        

    def llm_client(self,config :LlmConfig) -> ChatOpenAI:
        try:
            
            self.log(f"Creando el cliente ai con modelo {config.model}")
            return ChatOpenAI(
                name=config.name_agent,
                api_key= config.api_key,
                model= config.model,
                temperature= config.temperature,
            )
            
        except Exception as e:
            self.log(f"[ERROR] details: {e}")
            raise