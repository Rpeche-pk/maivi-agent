from typing import Dict, Callable
from llm.domain.llm_entities import LLMRequestConfig, LlmConfig
from llm.domain.llm_exceptions import ServiceLLMError, LLMServiceConfigurationError
from llm.domain.llm_service import LlmService
from llm.infrastructure.openai_client import OpenAIClient
from shared.init_logger import init_logger
from shared.config import settings

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


class OpenAiService(LlmService):
    
    def __init__(self):
        self.log = init_logger(self.__class__.__name__)
        self.llm = OpenAIClient()
        self._prompt_strategies: Dict[str, Callable[[str], ChatPromptTemplate]] = {
            "IMAGE": self._create_image_prompt,
            "TEXT": self._create_text_prompt,
        }

    async def set_llm_Service(self, llm_config: LLMRequestConfig) -> Runnable:
        
        self.log.info("[INFRASTRUCTURE] Create chain langchain prompt + llm + structure output")
        try:

            config_llm = LlmConfig(model=settings.MODEL_NAME)

            instance_llm = self.llm.llm_client(config=config_llm)

            if llm_config.tools:
                self.log.info("[INFRASTRUCTURE] Adding the tools to llm if required")
                instance_llm = instance_llm.bind_tools(llm_config.tools)

            if llm_config.structured_output:
                self.log.info("[INFRASTRUCTURE] establishing an output structure for the llm")
                instance_llm = instance_llm.with_structured_output(llm_config.structured_output)

            prompt = self._set_prompt_multimodal(llm_config.input_type.value, llm_config.prompt)
            
            self.log.debug("[INFRASTRUCTURE] establishing prompt")
        
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
            self.log.error(f"[ERROR] {error.to_dict()}")
            raise error

    def _create_image_prompt(self, prompt :str) -> ChatPromptTemplate:
        #prompt_system = PromptManager.get_prompt("SystemPrompts", "CLASSIFY_ASSISTANT")
        self.log.info(f"[INFRASTRUCTURE] Creating image prompt strategy for multimodal input.")

        system_message = SystemMessage(content= prompt)
        human_message = HumanMessage(content= [
            {"type": "text", "text": "{text_content}"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64,{image_base64}"
                },
            },
        ])
        
        prompt = ChatPromptTemplate(messages= [
            system_message,
            human_message
        ])
        return prompt

    def _create_text_prompt(self, prompt :str) -> ChatPromptTemplate:

        system_message = SystemMessage(content= prompt)
        human_message = HumanMessage(content= "{message_user}")

        prompt = ChatPromptTemplate(messages= [
            system_message,
            human_message
        ])
        return prompt


    
    def _set_prompt_multimodal(self, type : str, prompt : str) -> ChatPromptTemplate:
        stratefy = self._prompt_strategies.get(type)

        if not stratefy:
            raise ServiceLLMError(f"El tipo de prompt '{type}' no es válido.")

        return stratefy(prompt)