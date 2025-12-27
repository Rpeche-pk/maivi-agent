from llm.domain.llm_entities import LLMRequestConfig, LlmConfig
from llm.infrastructure.openai_client import OpenAIClient
from shared.init_logger import init_logger
from shared.config import settings

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, HumanMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class OpenAiService(OpenAIClient):
    
    def __init__(self):
        self.log = init_logger("open_ai_service")
        self.llm = OpenAIClient()
    
    def set_llm_Service(self,llm_config : LLMRequestConfig) -> Runnable:
        
        self.log("Create chain langchain prompt + llm + structure output")
        try:
            
            config_llm = LlmConfig(model= settings.MODEL_NAME)
            
            instance_llm = self.llm.llm_client(config= config_llm)
            
            if llm_config.tools:
                self.log("Adding the tools to llm if required")
                instance_llm = instance_llm.bind_tools(llm_config.tools)
                
            if llm_config.structured_output:
                self.log("establishing an output structure for the llm")
                instance_llm = instance_llm.with_structured_output(llm_config.structured_output)
                
            
        
        except Exception as e:
            self.log("[ERROR] details: {e}")
            raise
        
    def __set_prompt_multimodal(type : str, llm: ChatOpenAI):
        
        match (type):
            case "IMAGE":
                
                HumanMessage(content= [
                    {"type": "text", "text": "Describe any structural issues visible."},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64"
                    },
                ])
                prompt = ChatPromptTemplate(messages= [
                    
                ])
            case "TEXT":
                return ""
            case _:
                return ""