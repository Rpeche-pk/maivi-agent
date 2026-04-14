"""
Ejemplo de uso del sistema de reintentos con interrupt_before.

Este ejemplo demuestra cómo funciona el flujo completo de procesamiento
de recibos con reintentos automáticos cuando la clasificación falla.
"""

import asyncio
from maivi_agent.application.graph import get_workflow
from shared.init_logger import init_logger

log = init_logger("InterruptExample")


async def simulate_receipt_processing():
    """
    Simula el procesamiento de recibos con múltiples reintentos.
    En producción, esto sería llamado desde tu API cuando Baileys envíe imágenes.
    """
    
    # Obtener el grafo compilado con interrupt_before=["wait_for_image"]
    graph = get_workflow()
    
    # Configuración de sesión (thread_id único por usuario)
    phone_number = "573123456789"
    config = {"configurable": {"thread_id": phone_number}}
    
    log.info("=" * 60)
    log.info("INTENTO 1: Usuario envía primera imagen (borrosa)")
    log.info("=" * 60)
    
    # Estado inicial con la primera imagen
    initial_state = {
        "image_base64": "imagen_borrosa_base64...",  # En realidad sería base64 real
        "phone_number": phone_number,
        "intent_count": 0,
        "limit_intents": 3,
        "waiting_for_image": False,
        "is_valid": False,
        "service_type": None,
        "extracted_data": None,
        "message_user": ""
    }
    
    # Ejecutar el grafo
    result = await graph.ainvoke(initial_state, config)
    
    log.info(f"✅ Resultado intento 1:")
    log.info(f"   - service_type: {result.get('service_type')}")
    log.info(f"   - intent_count: {result.get('intent_count')}")
    log.info(f"   - waiting_for_image: {result.get('waiting_for_image')}")
    log.info(f"   - message_user: {result.get('message_user')}")
    
    # Verificar el estado del grafo
    current_state = graph.get_state(config)
    log.info(f"📍 Estado del grafo:")
    log.info(f"   - Próximo nodo: {current_state.next}")  # ["wait_for_image"] = está pausado
    log.info(f"   - Valores actuales: intent_count={current_state.values.get('intent_count')}")
    
    if current_state.next:
        log.info("")
        log.info("⏸️  GRAFO PAUSADO en wait_for_image - Esperando nueva imagen del usuario")
        log.info("")
        
        # Simular que el usuario envía una nueva imagen después de 2 segundos
        await asyncio.sleep(2)
        
        log.info("=" * 60)
        log.info("INTENTO 2: Usuario envía segunda imagen (más clara)")
        log.info("=" * 60)
        
        # Actualizar estado con nueva imagen
        updated_state = {
            **current_state.values,  # Preserva intent_count, limit_intents, etc.
            "image_base64": "imagen_clara_base64...",  # Nueva imagen
            "waiting_for_image": False  # Resetear flag
        }
        
        # Continuar desde donde se pausó
        result = await graph.ainvoke(updated_state, config)
        
        log.info(f"✅ Resultado intento 2:")
        log.info(f"   - service_type: {result.get('service_type')}")
        log.info(f"   - intent_count: {result.get('intent_count')}")
        log.info(f"   - is_valid: {result.get('is_valid')}")
        log.info(f"   - message_user: {result.get('message_user')}")
        
        # Verificar si el grafo terminó o sigue pausado
        final_state = graph.get_state(config)
        if final_state.next:
            log.info(f"⏸️  Grafo aún pausado en: {final_state.next}")
        else:
            log.info("🏁 Grafo completado exitosamente")
    
    else:
        log.info("🏁 Grafo completado en primer intento (imagen válida)")


async def simulate_max_retries():
    """
    Simula el caso donde el usuario alcanza el límite de 3 intentos.
    """
    log.info("\n\n")
    log.info("#" * 60)
    log.info("SIMULACIÓN: Límite de 3 intentos alcanzado")
    log.info("#" * 60)
    
    graph = get_workflow()
    config = {"configurable": {"thread_id": "573987654321"}}
    
    initial_state = {
        "image_base64": "imagen_invalida_1_base64...",
        "phone_number": "573987654321",
        "intent_count": 0,
        "limit_intents": 3,
        "waiting_for_image": False,
        "is_valid": False,
        "service_type": None,
        "extracted_data": None,
        "message_user": ""
    }
    
    for attempt in range(1, 4):
        log.info(f"\n🔄 Intento {attempt}/3")
        
        if attempt == 1:
            result = await graph.ainvoke(initial_state, config)
        else:
            current = graph.get_state(config)
            updated = {
                **current.values,
                "image_base64": f"imagen_invalida_{attempt}_base64...",
                "waiting_for_image": False
            }
            result = await graph.ainvoke(updated, config)
        
        log.info(f"   intent_count: {result.get('intent_count')}")
        log.info(f"   service_type: {result.get('service_type')}")
        
        state = graph.get_state(config)
        if not state.next:
            log.info(f"\n❌ Límite alcanzado. Flujo terminado.")
            log.info(f"   Mensaje final: {result.get('message_user')}")
            break
        
        await asyncio.sleep(1)


async def main():
    """Ejecutar ejemplos de uso."""
    
    # Ejemplo 1: Reintento exitoso en segundo intento
    await simulate_receipt_processing()
    
    # Ejemplo 2: Alcanzar límite de 3 intentos
    await simulate_max_retries()


if __name__ == "__main__":
    asyncio.run(main())
