from llm.domain.llm_entities import LLMRequestConfig, UserInputType
from llm.domain.llm_service import LlmService
from maivi_agent.domain.image_storage import ImageStorage
from maivi_agent.domain.receipts_repository import ReceiptsRepository
from maivi_agent.domain.state import ReceiptState
from maivi_agent.domain.entities import ClassifyModel, ExtractedData, ReceiptDataSave
from maivi_agent.infrastructure.whatsapp_service import WhatsAppService
from shared.init_logger import init_logger
from shared.prompts import PromptManager
from shared.config import settings
from langgraph.types import Command
from typing import Literal

class WorkFlowNodes:
    """class WorkFlowNodes"""
    
    def __init__(self,llm_service : LlmService, wsp_service: WhatsAppService, image_service: ImageStorage, receipts_repository:ReceiptsRepository):
        self.llm_service = llm_service
        self.wsp_service = wsp_service
        self.image_service = image_service
        self.receipts_repository = receipts_repository
        self.log = init_logger(self.__class__.__name__)

    
    async def classify_image_node(self, state: ReceiptState) -> Command[Literal["decision_nodes_with_interrupt","end_node"]]:
        self.log.info("[NODE] Classifying image node started.")

        if(state.get("waiting_for_image",False)):
            return Command(goto="end_node" ,update=state)

        try:
            request_config = LLMRequestConfig(
                input_type=UserInputType.IMAGE,
                image_base64=state["image_base64"],
                prompt= PromptManager.get_prompt("SystemPrompts","CLASSIFY_ASSISTANT").content.format(name_agent ="maivi"),
                structured_output= ClassifyModel
            )
            chain = await self.llm_service.set_llm_Service(request_config)
            
            result = await chain.ainvoke({
                "text_content": PromptManager.get_prompt("UserPrompts","BUILD_USER_PROMPT_IMAGE").content
            })
            self.log.info("[NODE] Classifying image node completed successfully.")
            
            return Command(update ={
                **state,
                "is_valid": True,
                "service_type": result.service.value,
                "waiting_for_image": False,
                "message_user": f"El recibo ha sido clasificado como {result.service.value}.",
            }, goto = "decision_nodes_with_interrupt")

        except Exception as e:
            self.log.error("[ERROR] Classifying image node. Details %s",e)
            return Command(update = {
                **state,
                "is_valid": False,
                "service_type": "NO_VALIDO",
                "waiting_for_image": False,
                "message_user": "Error al clasificar el recibo. Por favor, intente nuevamente más tarde."
            }, goto = "end_node")

    def decision_nodes_with_interrupt(self, state: ReceiptState) -> Command[Literal["data_extraction_node","max_intent_limit_node","max_intent_node"]]:
        self.log.info("[NODE] Decision node with interrupt started.")
        
        intent_count = state.get("intent_count", 0)
        limit_intents = state.get("limit_intents", 3)
        classification = state.get("service_type", "NO_VALIDO")
        
        if classification in ["AGUA","LUZ","GAS"]:
            return Command(goto="data_extraction_node")
        
        if intent_count >= limit_intents:
            return Command(goto="max_intent_limit_node")
        
        return Command(goto="max_intent_node")


    async def data_extraction_node(self, state: ReceiptState) -> Command[Literal["persistence_data_node"]]:
        self.log.info("[NODE - data_extraction_node] start flow node data extraction from receipt. <<%s>>",state.get("service_type"),None)
        
        promptSystem = PromptManager.get_prompt("SystemPrompts","PROMPT_EXTRACT_DATA").content
        
        config = LLMRequestConfig(
            image_base64=state.get("image_base64"),
            input_type=UserInputType.IMAGE,
            temperature=0,
            prompt= promptSystem.format(name_agent=settings.NAME_AGENT),
            structured_output=ExtractedData
        )
        
        response = await self.llm_service.set_llm_Service(config)
        
        result = await response.ainvoke({
                "text_content": PromptManager.get_prompt("UserPrompts","USER_PROMPT_EXTRACT_DATA").content
            })
        
        self.log.info("[NODE - data_extraction_node] Extraction from the receiving flow node, completed successfully")
        
        return Command(
            update= {
                **state,
                "extracted_data": result
            },
            goto ="upload_image_node"
        )
    
    async def upload_image_node(self, state: ReceiptState) -> Command[Literal["persistence_data_node"]]:

        self.log.info("[NODE - upload_image_node] Start node upload image node")
        
        image_base64= state.get("image_base64")
        file_name= state.get("service_type","RECEIPT")
        tag = state.get("service_type")
        
        url = await self.image_service.upload_image(file_doc=image_base64, file_name=file_name,tags= tag)
        
        self.log.info("[NODE - upload_image_node] Finish node upload image node success")
        
        return Command(update={
            **state,
            "image_base64" : url
        }, goto="persistence_data_node")

    def persistence_data_node(self, state: ReceiptState) -> Command[Literal["send_confirmation_node"]]:
        
        self.log.info("[NODE - persistence_data_node] start of execution of the persistence node")
        
        extracted_data = state.get("extracted_data", ExtractedData())
        
        body = ReceiptDataSave(
            phone_number= state.get("phone_number"),
            service_type= state.get("service_type"),
            is_valid= state.get("is_valid", False),
            is_notified= False,
            amount_total= extracted_data.amount_total,
            date_expired= extracted_data.date_expired,
            consumption_period= extracted_data.consumption_period,
            company= extracted_data.company,
            link_receipt_image= state.get("image_base64")
        )
        
        response = self.receipts_repository.save_receipt(body)
        
        self.log.info("[NODE - persistence_data_node] Receipt data saved successfully. ID: %s",response)
        
        return Command(update=state, goto="send_confirmation_node")
    
    def send_confirmation_node(self, state: ReceiptState) -> Command[Literal["end_node"]]:
        self.log.info("[NODE] Sending confirmation message to user.")
        
        data_extracted = state.get("extracted_data",ExtractedData())
        
        type_service = {"LUZ": "💡", "AGUA": "💧", "GAS": "🔥"}.get(state["service_type"], "📄")
        
        message = f"""✅ Tu recibo ha sido procesado exitosamente.
        
        Detalles:
        - Tipo de servicio: {type_service} {state.get('service_type')}
        - Monto total a pagar: {data_extracted.amount_total if data_extracted else 'N/A'}
        - Fecha de vencimiento: {data_extracted.date_expired if data_extracted else 'N/A'}
        - Período de consumo: {data_extracted.consumption_period if data_extracted else 'N/A'}
        - Compañía: {data_extracted.company if data_extracted else 'N/A'}
        
        Gracias por usar Maivi, tu asistente de gestión de recibos."""
    
        return Command( update={
            **state,
            "message_user": message
        }, goto="end_node")

        
    def max_intent_node(self, state: ReceiptState) -> Command[Literal["classify_image_node"]]:
        self.log.info(f"[NODE] Max intent validation. Intent {state.get('intent_count', 0)+1} of {state.get('limit_intents', 3)}.")
        intent_count = state.get("intent_count", 0) + 1
        limit_intents = state.get("limit_intents", 3)
        
        if intent_count >= limit_intents:
            self.log.info("[NODE] Max intents reached. Ending flow.")
            state["message_user"] = "Has alcanzado el número máximo de intentos. Por favor, contacta con soporte si necesitas ayuda."
        else:
            self.log.info(f"[NODE] Attempt {intent_count}/{limit_intents}. Requesting new image.")
            state["message_user"] = "La imagen no pudo ser clasificada. Por favor, envía una imagen más clara del recibo."
            
        self.wsp_service.send_message(
            to=state.get("phone_number"),
            message=state["message_user"]
        )
        
        return Command(goto="classify_image_node",
            update={
            **state,
            "intent_count": intent_count,
            "waiting_for_image": True,
            "image_base64": ""
        })
        
    def max_intent_limit_node(self, state: ReceiptState) -> ReceiptState:
        message = f"""❌ Lo siento, no pude procesar tu recibo después de {state.get('limit_intents', 3)} intentos.

        Por favor:
        1. Asegúrate de que la imagen sea clara
        2. Que sea un recibo de agua, luz o gas
        3. Intenta con mejor iluminación

        Escribe "ayuda" si necesitas más información."""
        
        self.wsp_service.send_message(
            to=state.get("phone_number"),
            message=message
        )
        return {
            **state,
            "is_valid": False,
            "message_user": message
        }


    def end_node(self, state: ReceiptState) -> ReceiptState:
        """Nodo final que envía el mensaje final al usuario."""
        self.log.info("[NODE] End node - Sending final message.")
        
        self.wsp_service.send_message(
            to=state.get("phone_number"),
            message=state["message_user"]
        )
        
        return state

'''
    OPCION B USANDO INTERRUP_BEFORE WITH MEMORY
    def data_extraction_node(self, state: ReceiptState) -> Command[Literal["max_intent_node","extracted_data_node"]]:
        self.log.info("[NODE] Validating classification node started.")
        try:
            if state["service_type"] == "NO_VALIDO" or state["service_type"] is None:
                self.log.info("[NODE] Validation failed: Service type is NO_VALIDO or None.")
                return Command(
                    goto= "max_intent_node",
                    update= {
                        **state,
                        "is_valid": False,
                        "message_user": "El recibo no es válido para su procesamiento.",
                    }
                )

            self.log.info("[NODE] Validation successful.")
            return Command( 
                goto= "extracted_data_node",
                update={
                **state,
                "is_valid": True,
                "message_user": f"El recibo ha sido validado como {state['service_type']}."
            })
        except Exception as e:
            self.log.error("[ERROR] Validating classification node. Details %s",e)
            return {
                **state,
                "is_valid": False,
                "message_user": "Error al validar la clasificación del recibo. Por favor, intente nuevamente más tarde."
            }

    def max_intent_node(self, state: ReceiptState) -> Command[Literal["request_new_image_node","end_node"]]:
        """Verifica si se ha alcanzado el máximo de intentos."""
        intent_count = state.get("intent_count", 0) + 1
        limit_intents = state.get("limit_intents", 3)
        self.log.info(f"[NODE] Max intent validation. Intent {intent_count} of {limit_intents}.")
        
        if intent_count >= limit_intents:
            self.log.info("[NODE] Max intents reached. Ending flow.")
            return Command(
                goto="end_node",
                update={
                    **state,
                    "intent_count": intent_count,
                    "is_valid": False,
                    "message_user": "Has alcanzado el número máximo de intentos. Por favor, contacta con soporte si necesitas ayuda."
                }
            )

        # Si no se alcanzó el límite, solicitar nueva imagen
        self.log.info(f"[NODE] Attempt {intent_count}/{limit_intents}. Requesting new image.")
        return Command(
            goto="request_new_image_node",
            update={
                **state,
                "intent_count": intent_count,
                "waiting_for_image": True,
                "image_base64": "",
                "message_user": f"La imagen no pudo ser clasificada. Por favor, envía una imagen más clara del recibo. Intento {intent_count} de {limit_intents}."
            }
        )

    def request_new_image_node(self, state: ReceiptState) -> Command[Literal["wait_for_image"]]:
        """Solicita al usuario que envíe una nueva imagen."""
        self.log.info("[NODE] Requesting new image from user.")
        
        # Enviar mensaje al usuario solicitando nueva imagen
        self.wsp_service.send_message(
            to=state.get("phone_number"),
            message=state["message_user"]
        )
        
        # Ir al nodo de espera (se interrumpirá automáticamente)
        return Command(
            goto="wait_for_image",
            update=state
        )

    def wait_for_image(self, state: ReceiptState) -> Command[Literal["classify_image_node"]]:
        """
        Nodo de espera para nueva imagen del usuario.
        
        Este nodo se interrumpirá automáticamente cuando se compile el grafo
        con interrupt_before=["wait_for_image"].
        
        Cuando el usuario envíe una nueva imagen desde WhatsApp, el grafo
        se reanudará desde aquí y volverá a clasificar la imagen.
        """
        self.log.info("[NODE] Waiting for new image from user...")
        
        # Cuando llegue nueva imagen, volver a clasificar
        return Command(
            goto="classify_image_node",
            update={
                **state,
                "waiting_for_image": False
            }
        )
    
    def end_node(self, state: ReceiptState) -> dict[str, any]:
        """Nodo final que envía el mensaje final al usuario."""
        self.log.info("[NODE] End node - Sending final message.")
        
        self.wsp_service.send_message(
            to=state.get("phone_number"),
            message=state["message_user"]
        )
        
        return state
 '''


