import base64
from typing import Dict, Callable
from llm.domain.llm_entities import LLMRequestConfig, LlmConfig
from llm.domain.llm_exceptions import ServiceLLMError, LLMServiceConfigurationError
from llm.domain.llm_service import LlmService
from llm.infrastructure.openai_client import OpenAIClient
from shared.init_logger import init_logger
from shared.config import settings

from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class OpenAiService(LlmService):
    
    def __init__(self):
        self.log = init_logger(self.__class__.__name__)
        self.llm = OpenAIClient()
        self._prompt_strategies: Dict[str, Callable] = {
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

            prompt = self._set_prompt_multimodal(llm_config.input_type.value, llm_config.prompt, image_base64=llm_config.image_base64)
            
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

    def _create_image_prompt(self, system_prompt: str, image_base64: str = None, image_path: str = None) -> ChatPromptTemplate:
        """Crea un prompt multimodal con imagen.
        
        Args:
            system_prompt: El prompt del sistema
            image_base64: Imagen ya codificada en base64 (opcional)
            image_path: Ruta a la imagen para codificar (opcional)
        """
        self.log.info(f"[INFRASTRUCTURE] Creating image prompt strategy for multimodal input.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", [
                {"type": "text", "text": "{text_content}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ])
        ])
        return prompt

    def _create_text_prompt(self, system_prompt: str, **kwargs) -> ChatPromptTemplate:
        """Crea un prompt de solo texto.
        
        Args:
            system_prompt: El prompt del sistema
            **kwargs: Argumentos adicionales (ignorados para compatibilidad)
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text_content}")
        ])
        return prompt


    
    def _set_prompt_multimodal(self, type: str, system_prompt: str, **kwargs) -> ChatPromptTemplate:
        """Configura el prompt según el tipo (IMAGE o TEXT).
        
        Args:
            type: Tipo de prompt (IMAGE o TEXT)
            system_prompt: El prompt del sistema
            **kwargs: Argumentos adicionales como image_base64, image_path, etc.
        """
        strategy = self._prompt_strategies.get(type)

        if not strategy:
            raise ServiceLLMError(f"El tipo de prompt '{type}' no es válido.")

        return strategy(system_prompt, **kwargs)