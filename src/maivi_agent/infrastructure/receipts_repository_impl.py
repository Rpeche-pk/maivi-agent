import pymongo
from bson import ObjectId
from maivi_agent.domain.entities import ReceiptDataSave
from maivi_agent.domain.receipts_repository import ReceiptsRepository
from maivi_agent.domain.receipts_exceptions import (
    ReceiptSaveError,
    ReceiptUpdateError,
    ReceiptQueryError,
    DatabaseConnectionError,
    ReceiptNotFoundError,
)
from shared.config import settings

class ReceiptsRepositoryImpl(ReceiptsRepository):
    
    def __init__(self):
        self.db = self._init_database()
        
    def _init_database(self) -> pymongo.collection.Collection:
        try:
            client = pymongo.MongoClient(settings.DATABASE_URL)
            database = client.get_database(settings.DATABASE_NAME)
            collection = database.get_collection(settings.COLLECTION_NAME)
            return collection
        except Exception as e:
            raise DatabaseConnectionError(original_error=e)

    def save_receipt(self, receipt_data: ReceiptDataSave) -> str:
        try:
            data = receipt_data if isinstance(receipt_data, dict) else receipt_data.model_dump(mode='json')
            result = self.db.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise ReceiptSaveError(original_error=e)

    def get_receipts_by_service(self, phone_number: str, service_type: str) -> list[ReceiptDataSave]:
        try:
            receipts = self.db.find({
                "phone_number": phone_number,
                "service_type": service_type
            })
            return [ReceiptDataSave(**receipt) for receipt in receipts]
        except Exception as e:
            raise ReceiptQueryError("get_receipts_by_service", original_error=e)

    def mark_as_notified(self, receipt_id: str) -> None:
        try:
            result = self.db.update_one(
                {"_id": ObjectId(receipt_id)},
                {"$set": {"notified": True}}
            )
            if result.matched_count == 0:
                raise ReceiptNotFoundError(receipt_id)
        except ReceiptNotFoundError:
            raise
        except Exception as e:
            raise ReceiptUpdateError(receipt_id, original_error=e)

    def obtain_receipt_expire_by_date(self, date_expired: str) -> list[ReceiptDataSave]:
        try:
            receipts = self.db.find({
                "expiration_date": date_expired,
                "notified": {"$ne": True}
            })
            return [ReceiptDataSave(**receipt) for receipt in receipts]
        except Exception as e:
            raise ReceiptQueryError("obtain_receipt_expire_by_date", original_error=e)