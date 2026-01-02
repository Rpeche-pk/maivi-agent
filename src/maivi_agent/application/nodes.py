from llm.domain.llm_service import LlmService
from shared import init_logger

class WorkFlowNodes:
    """class WorkFlowNodes"""
    
    def __init__(self,llm_service : LlmService):
        self.llm_service = llm_service
        self.log = init_logger(self.__class__.__name__)
        
    
    