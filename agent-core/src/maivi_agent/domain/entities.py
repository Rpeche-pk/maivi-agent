from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Service(Enum):
    AGUA = "AGUA"
    LUZ = "LUZ"
    GAS = "GAS"
    NO_VALIDO = "NO_VALIDO"


class ClassifyModel(BaseModel):
    service : Service = Field(description= "Servicio de AGUA, LUZ, GAS o NO_VALIDO")
        

class ExtractedData(BaseModel):
    """Entidad para los datos extraídos del recibo procesado.
    
    Total a pagar
    fecha vencimiento
    Periodo consumo
    Compañía (ELECTRODUNAS, EMAPICA, CONTUGAS)
    """
    amount_total : float = Field(description="Monto total a pagar del recibo")
    date_expired: str = Field(description="Fecha de vencimiento del recibo en el formato dd/MM/yyyy. Ejm: 10/05/2025")
    consumption_period : str =  Field(description="Período de consumo (ej: Octubre 2024)")
    company : Optional[str] = Field(description="Nombre de la compañia el cual factura el recibo")

class ReceiptDataSave(BaseModel):
    """Entidad para almacenar datos del recibo procesado."""
    #id_receipt: Optional[str] = Field(description="ID único del recibo en la base de datos")
    phone_number: str = Field(description="Número de teléfono del usuario (sin @s.whatsapp.net)")
    service_type: Service = Field(description="Tipo de servicio clasificado")
    is_valid: bool = Field(description="Indica si el recibo es válido")
    is_notified : bool = Field(description="Indica si el usuario fue notificado del resultado del procesamiento")
    created_at: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
    amount_total : Optional[float] = Field(description="Monto total a pagar del recibo")
    date_expired: Optional[str] = Field(description="Fecha de vencimiento del recibo en el formato dd/MM/yyyy. Ejm: 10/05/2025")
    consumption_period : Optional[str] =  Field(description="Período de consumo (ej: Octubre 2024)")
    company : Optional[str] = Field(description="Nombre de la compañia el cual factura el recibo")
    link_receipt_image : Optional[str] = Field(description="Link a la imagen del recibo almacenada")