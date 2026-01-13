from abc import abstractmethod

import pymongo
from maivi_agent.domain.entities import ReceiptDataSave
from maivi_agent.domain.receipts_repository import ReceiptsRepository
from shared.config import settings

class ReceiptsRepositoryImpl(ReceiptsRepository):
    
    def __init__(self):
        self.db = self._init_database()
        
    def _init_database(self):
        client = pymongo.MongoClient(settings.DATABASE_URL)
        database = client.get_database(settings.DATABASE_NAME)
        collection = database.get_collection(settings.COLLECTION_NAME)
        
        return collection
    
    async def save_receipt(self, receipt_data: ReceiptDataSave) -> str:
        
        pass
    
    
    async def get_receipts_by_service(self, phone_number: str, service_type: str) -> list[ReceiptDataSave]:
        pass

    async def mark_as_notified(self, receipt_id: str) -> None:
        pass

    async def obtain_receipt_expire_by_date(self, date_expired: str) -> list[ReceiptDataSave]:
        pass