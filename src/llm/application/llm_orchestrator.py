from llm.domain.llm_entities import LLMRequestConfig
from llm.domain.llm_exceptions import ServiceLLMError
from llm.domain.llm_service import LlmService
from shared import init_logger
from langchain_core.runnables import Runnable

class LlmOrchestrator:

    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service
        self.log = init_logger("llm_orchestrator")
        

    async def execute_llm(self, request: LLMRequestConfig) -> Runnable:
        
        self.log.info("[APPLICATION] - Executing LLM service with provided configuration")
        try:

            chain = await self.llm_service.set_llm_Service(request)

            return chain
        except Exception as e:
            self.log.error(f"[ERROR] {e}")
            raise ServiceLLMError(
                message="Error executing LLM service",
                original_error=e,
                context={
                    "service": "LlmOrchestrator",
                    "method": "execute_llm"
                }
            )