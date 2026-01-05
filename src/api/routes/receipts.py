"""
API endpoint para recibir imágenes desde Baileys/WhatsApp.

Este módulo maneja:
1. Recepción de primera imagen (inicia nuevo grafo)
2. Recepción de reintentos (continúa grafo pausado)
3. Preservación de estado entre reintentos usando checkpointer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from maivi_agent.application.graph import get_workflow
from shared.init_logger import init_logger

router = APIRouter(prefix="/api/receipts", tags=["receipts"])
log = init_logger("ReceiptsAPI")


class ImageRequest(BaseModel):
    """Request para procesar imagen desde WhatsApp."""
    phone_number: str = Field(..., description="Número de teléfono del usuario (sin @s.whatsapp.net)")
    image_base64: str = Field(..., description="Imagen del recibo codificada en base64")


class ProcessResponse(BaseModel):
    """Response del procesamiento de imagen."""
    status: str
    phone_number: str
    service_type: Optional[str]
    is_valid: bool
    waiting_for_image: bool
    intent_count: int
    message: str
    next_nodes: Optional[list] = None  # Para debugging


@router.post("/process", response_model=ProcessResponse)
async def process_receipt_image(request: ImageRequest):
    """
    Endpoint principal para procesar imágenes de recibos.
    
    Flujo:
    1. Si es primera imagen del usuario → Inicia nuevo grafo
    2. Si el grafo está pausado esperando imagen → Continúa desde donde se pausó
    3. Si clasificación falla → Pausa en wait_for_image (gracias a interrupt_before)
    4. Usuario envía nueva imagen → Este endpoint la recibe y continúa el grafo
    
    Args:
        request: Datos de la imagen desde Baileys
        
    Returns:
        ProcessResponse: Estado actual del procesamiento
        
    Raises:
        HTTPException: Si hay error en el procesamiento
    """
    try:
        log.info(f"📩 Recibida imagen de {request.phone_number}")
        
        # Obtener grafo compilado con interrupt_before
        graph = get_workflow()
        config = {"configurable": {"thread_id": request.phone_number}}
        
        # 🔍 Verificar si hay un grafo pausado para este usuario
        current_state = graph.get_state(config)
        
        if current_state.next:  # ⭐ Hay un grafo pausado esperando
            log.info(f"🔄 REINTENTO - Usuario {request.phone_number} envió nueva imagen")
            log.info(f"   Grafo pausado en: {current_state.next}")
            log.info(f"   Intentos previos: {current_state.values.get('intent_count', 0)}")
            
            # Actualizar estado con la NUEVA imagen
            updated_state = {
                **current_state.values,  # ✅ Preserva intent_count, limit_intents, phone_number, etc.
                "image_base64": request.image_base64,  # 🔄 Nueva imagen del usuario
                "waiting_for_image": False  # ✅ Resetear flag de espera
            }
            
            # ▶️ CONTINUAR ejecución desde wait_for_image
            log.info("▶️  Continuando grafo desde la interrupción...")
            result = await graph.ainvoke(updated_state, config)
            
            # Verificar si se pausó otra vez (clasificación falló de nuevo)
            final_state = graph.get_state(config)
            log.info(f"   Resultado: service_type={result.get('service_type')}, "
                    f"intent_count={result.get('intent_count')}")
            
            if final_state.next:
                log.info(f"⏸️  Grafo pausado nuevamente en: {final_state.next}")
            else:
                log.info("🏁 Grafo completado para este usuario")
            
        else:  # 🆕 Primera imagen del usuario (nueva sesión)
            log.info(f"🆕 NUEVA SESIÓN - Usuario {request.phone_number} envió primera imagen")
            
            initial_state = {
                "image_base64": request.image_base64,
                "phone_number": request.phone_number,
                "intent_count": 0,
                "limit_intents": 3,
                "waiting_for_image": False,
                "is_valid": False,
                "service_type": None,
                "extracted_data": None,
                "message_user": ""
            }
            
            log.info("▶️  Iniciando nuevo grafo...")
            result = await graph.ainvoke(initial_state, config)
            
            # Verificar si se pausó (clasificación falló)
            final_state = graph.get_state(config)
            log.info(f"   Resultado: service_type={result.get('service_type')}, "
                    f"intent_count={result.get('intent_count')}")
            
            if final_state.next:
                log.info(f"⏸️  Grafo pausado en: {final_state.next} - Esperando reintento")
            else:
                log.info("🏁 Grafo completado en primer intento")
        
        # 📤 Preparar respuesta
        final_state = graph.get_state(config)
        
        response = ProcessResponse(
            status="success",
            phone_number=request.phone_number,
            service_type=result.get("service_type"),
            is_valid=result.get("is_valid", False),
            waiting_for_image=result.get("waiting_for_image", False),
            intent_count=result.get("intent_count", 0),
            message=result.get("message_user", ""),
            next_nodes=final_state.next if final_state.next else None
        )
        
        log.info(f"✅ Respuesta enviada: status={response.status}, "
                f"service_type={response.service_type}, "
                f"waiting={response.waiting_for_image}")
        
        return response
        
    except Exception as e:
        log.error(f"❌ Error procesando imagen de {request.phone_number}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar el recibo: {str(e)}"
        )


@router.get("/session/{phone_number}")
async def get_session_status(phone_number: str):
    """
    Obtiene el estado actual de la sesión de un usuario.
    Útil para debugging y monitoreo.
    
    Args:
        phone_number: Número de teléfono del usuario
        
    Returns:
        Estado actual del grafo para ese usuario
    """
    try:
        graph = get_workflow()
        config = {"configurable": {"thread_id": phone_number}}
        
        state = graph.get_state(config)
        
        if not state.values:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró sesión activa para {phone_number}"
            )
        
        return {
            "phone_number": phone_number,
            "current_state": state.values,
            "next_nodes": state.next,
            "is_paused": bool(state.next),
            "metadata": state.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error obteniendo sesión de {phone_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{phone_number}")
async def clear_session(phone_number: str):
    """
    Limpia la sesión de un usuario.
    Útil para resetear el estado cuando algo falla.
    
    Args:
        phone_number: Número de teléfono del usuario
        
    Returns:
        Confirmación de limpieza
    """
    try:
        # Nota: MemorySaver no tiene método para eliminar sesiones
        # En producción con Redis/PostgreSQL podrías implementar esto
        log.info(f"🗑️  Solicitud de limpieza de sesión para {phone_number}")
        
        return {
            "status": "success",
            "message": f"Sesión de {phone_number} marcada para limpieza. "
                      "Con MemorySaver se limpiará al reiniciar el servidor."
        }
        
    except Exception as e:
        log.error(f"Error limpiando sesión de {phone_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
