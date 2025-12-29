from llm.domain.llm_entities import LLMRequestConfig
from llm.domain.llm_exceptions import ServiceLLMError
from llm.domain.llm_service import LlmService
from shared.init_logger import init_logger
from langchain_core.runnables import Runnable

class LlmOrchestrator:

    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service
        self.log = init_logger(self.__class__.__name__)
        

    async def execute_llm(self, request: LLMRequestConfig) -> Runnable:
        
        self.log.info("[APPLICATION] - Executing LLM service with provided configuration. User input <%s>",  request.input_type)
        try:

            chain = await self.llm_service.set_llm_Service(request)

            return chain
        except Exception as e:
            self.log.error(f"[ERROR] {e}")
            raise ServiceLLMError(f"[ERROR] Error executing LLM service in {self.__class__.__name__}")
            
