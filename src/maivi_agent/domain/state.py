from typing import Optional, TypedDict, Literal


class ReceiptState(TypedDict):
    """Estado del grafo para procesamiento de recibos"""
    #input usuer
    image_base64 : str
    phone_number : str
    
    #clasification
    service_type : Optional[Literal["AGUA","LUZ","GAS", "NO_VALIDO"]]
    
    #Extracttion data
    extracted_data :  Optional[dict]
    
    #Validation
    is_valid : bool
    validation_errors : list[str]