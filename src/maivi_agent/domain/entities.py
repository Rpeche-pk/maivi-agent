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
    """
    Total a pagar
    fecha vencimiento
    Periodo consumo
    Compañía (ELECTRODUNAS, EMAPICA, CONTUGAS)
    """
    amount_total : float = Field(description="Monto total a pagar del recibo")
    date_expired: str = Field(description="Fecha de vencimiento del recibo en el formato dd/MM/yyyy. Ejm: 10/05/2025")
    consumption_period : str =  Field(description="Período de consumo (ej: Octubre 2024)")
    company : Optional[str] = Field(description="Nombre de la compañia el cual factura el recibo")