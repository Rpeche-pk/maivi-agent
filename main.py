"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import asyncio
from llm.infrastructure import get_container
from llm.domain.llm_entities import LLMRequestConfig, UserInputType


async def classify_receipt_example():
    """Ejemplo de clasificación de recibo usando el contenedor de dependencias."""
    
    # Obtener el contenedor con todas las dependencias (Singleton)
    container = get_container()
    
    # El orquestador ya tiene todas sus dependencias inyectadas
    orchestrator = container.llm_orchestrator
    
    # Configurar la solicitud para clasificación de texto
    request_config = LLMRequestConfig(
        input_type=UserInputType.TEXT,
        prompt="Clasificar tipo de recibo",
        temperature=0.0
    )
    
    # Ejecutar el LLM
    chain = await orchestrator.execute_llm(request_config)
    
    # Invocar la cadena con un mensaje de prueba
    result = await chain.ainvoke({
        "message_user": "Este es un recibo de ElectroDunas con consumo eléctrico"
    })
    
    print(f"Resultado de clasificación: {result}")


def main():
    """Función principal de la aplicación."""
    print("=" * 60)
    print("MAIVI AGENT - Sistema de Clasificación de Recibos")
    print("=" * 60)
    
    # Ejecutar ejemplo de clasificación
    asyncio.run(classify_receipt_example())
    
    print("=" * 60)
    print("Aplicación finalizada")
    print("=" * 60)


if __name__ == "__main__":
    main()
