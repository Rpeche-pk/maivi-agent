from typing import Optional
from llm.application.llm_orchestrator import LlmOrchestrator
from llm.domain.llm_client import LlmClient
from llm.domain.llm_service import LlmService
from llm.infrastructure.openai_client import OpenAIClient
from llm.infrastructure.openai_service import OpenAiService
from maivi_agent.infrastructure.whatsapp_service import WhatsAppService
from shared.init_logger import init_logger


class Container:
    
    def __init__(self):
        self.log = init_logger(self.__class__.__name__)
        self.log.info("[CONTAINER] Initializing dependency container")
        self._openai_client: Optional[LlmClient] = None
        self._openai_service: Optional[LlmService] = None
        self._llm_orchestrator: Optional[LlmOrchestrator] = None
        self._wsp_service: Optional[WhatsAppService] = None
        self.log.info("[CONTAINER] Dependency container initialized successfully")
    
    
    @property
    def instance_openai_client(self) -> LlmClient:
        """
        Get or create OpenAI client instance (Singleton).
        
        Returns:
            OpenAIClient: Singleton instance of OpenAI client
        """
        if self._openai_client is None:
            self.log.info("[CONTAINER] Creating OpenAI client instance")
            self._openai_client = OpenAIClient()
        return self._openai_client
        
    @property
    def instance_openai_service(self) -> LlmService:
        """
        Get or create LLM service instance (Singleton).
        
        Returns:
            LlmService: Singleton instance of LLM service (OpenAiService)
        """
        if self._openai_service is None:
            self.log.info("[CONTAINER] Creating OpenAI service instance")
            self._openai_service = OpenAiService()
            
        return self._openai_service
    
    @property
    def llm_orchestrator(self) -> LlmOrchestrator:
        """
        Get or create LLM orchestrator instance (Singleton).
        
        Returns:
            LlmOrchestrator: Singleton instance of LLM orchestrator
        """
        if self._llm_orchestrator is None:
            self.log.info("[CONTAINER] Creating LLM orchestrator instance")
            self._llm_orchestrator = LlmOrchestrator(llm_service=self.instance_openai_service)
            
        return self._llm_orchestrator

    
    @property
    def wsp_service(self) -> WhatsAppService:
        """
        Get or create WhatsApp service instance (Singleton).
        
        Returns:
            WhatsAppService: Singleton instance of WhatsApp service
        """
        if self._wsp_service is None:
            self.log.info("[CONTAINER] Creating WhatsApp service instance")
            self._wsp_service = WhatsAppService()
            
        return self._wsp_service
    
instance = None

def get_container() -> Container:
    """
    Get the singleton instance of the dependency container.
    
    Returns:
        Container: Singleton instance of the dependency container
    """
    global instance
    if instance is None:
        instance = Container()
    return instance