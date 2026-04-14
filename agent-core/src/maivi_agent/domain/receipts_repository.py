from abc import ABC, abstractmethod
from maivi_agent.domain.entities import ReceiptDataSave

class ReceiptsRepository(ABC):
    """Repositorio abstracto para la gestión de recibos procesados."""
    @abstractmethod
    def save_receipt(self, receipt_data: ReceiptDataSave) -> str:
        """
        Guarda los datos del recibo procesado en el repositorio.
        Args:
            receipt_data (ReceiptDataSave): Datos del recibo a guardar.
        Returns:
            str: ID único del recibo guardado.
        """
        pass
    
    @abstractmethod
    def get_receipts_by_service(self, phone_number: str, service_type: str) -> list[ReceiptDataSave]:
        """
        Obtiene los recibos procesados por tipo de servicio para un usuario específico.
        Args:
            phone_number (str): Número de teléfono del usuario.
            service_type (str): Tipo de servicio (AGUA, LUZ, GAS).
        Returns:
            list[ReceiptDataSave]: Lista de recibos procesados."""
        pass
    
    @abstractmethod
    def mark_as_notified(self, receipt_id: str) -> None:
        """Marca un recibo como notificado al usuario.
        Args:
            receipt_id (str): ID del recibo a marcar.
        """
        pass
    
    @abstractmethod
    def obtain_receipt_expire_by_date(self, date_expired: str) -> list[ReceiptDataSave]:
        """Obtiene los recibos que vencen en una fecha específica.
        Args:
            date_expired (str): Fecha de vencimiento en formato dd/MM/yyyy.
        Returns:
            list[ReceiptDataSave]: Lista de recibos que vencen en la fecha dada.
        """
        pass