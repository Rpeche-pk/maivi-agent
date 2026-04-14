from typing import Optional, TypedDict, Literal


class ReceiptState(TypedDict):
    """Estado del grafo para procesamiento de recibos"""
    #input usuer
    image_base64 : str
    phone_number : str
    
    #Validation
    is_valid : bool
    message_user : str
    
    #loop
    intent_count : int
    limit_intents : int
    waiting_for_image : Optional[bool]  # Flag para indicar que estamos esperando nueva imagen
    
    #clasification
    service_type : Optional[Literal["AGUA","LUZ","GAS", "NO_VALIDO"]]
    
    #Extracttion data
    extracted_data :  Optional[dict]