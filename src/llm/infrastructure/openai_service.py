from typing import Dict
from llm.domain.llm_entities import LLMRequestConfig, LlmConfig
from llm.domain.llm_exceptions import ServiceLLMError, LLMServiceConfigurationError
from llm.infrastructure.openai_client import OpenAIClient
from shared.init_logger import init_logger
from shared.config import settings

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

class OpenAiService(OpenAIClient):
    
    def __init__(self):
        self.log = init_logger("open_ai_service")
        self.llm = OpenAIClient()
        self._prompt_strategies: Dict[str, ChatPromptTemplate] = {
            "IMAGE": self._create_image_prompt,
            "TEXT": self._create_text_prompt,
        }
    
    def set_llm_Service(self, llm_config: LLMRequestConfig) -> Runnable:
        
        self.log("Create chain langchain prompt + llm + structure output")
        try:
            
            config_llm = LlmConfig(model=settings.MODEL_NAME)
            
            instance_llm = self.llm.llm_client(config=config_llm)
            
            if llm_config.tools:
                self.log("Adding the tools to llm if required")
                instance_llm = instance_llm.bind_tools(llm_config.tools)
                
            if llm_config.structured_output:
                self.log("establishing an output structure for the llm")
                instance_llm = instance_llm.with_structured_output(llm_config.structured_output)
                
            prompt = self._set_prompt_multimodal(llm_config.input_type.value)
        
            chain = prompt | instance_llm
            
            return chain
        
        except Exception as e:
            error = LLMServiceConfigurationError(
                message="Failed to configure LLM service",
                model_name=settings.MODEL_NAME,
                has_tools=bool(llm_config.tools),
                has_structured_output=bool(llm_config.structured_output),
                original_error=e,
                context={
                    "service": "OpenAiService",
                    "method": "set_llm_Service"
                }
            )
            self.log(f"[ERROR] {error.to_dict()}")
            raise error
    
    def _create_image_prompt(self) -> ChatPromptTemplate:
        
        system_message = SystemMessage(content="You are a helpful assistant that helps people find information.")
        
        human_message = HumanMessage(content= [
            {"type": "text", "text": "{text_content}"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64,{message_user}"
                },
            },
        ])
        prompt = ChatPromptTemplate(messages= [
            system_message,
            human_message
        ])
        return prompt
    
    def _create_text_prompt(self) -> ChatPromptTemplate:
        
        system_message = SystemMessage(content="You are a helpful assistant that helps people find information.")
        human_message = HumanMessage(content= "{message_user}")
        
        prompt = ChatPromptTemplate(messages= [
            system_message,
            human_message
        ])
        return prompt


    
    def _set_prompt_multimodal(self, type : str) -> ChatPromptTemplate:
        stratefy = self._prompt_strategies.get(type)
        
        if not stratefy:
            raise ServiceLLMError(f"El tipo de prompt '{type}' no es válido.")
        
        return stratefy()
        
        