from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from maivi_agent.domain.state import ReceiptState
from maivi_agent.application.nodes import WorkFlowNodes
from maivi_agent.infrastructure.container import get_container
from shared.init_logger import init_logger


log = init_logger("ReceiptWorkflow")


def create_receipt_workflow():
    """
    Crea y compila el grafo de procesamiento de recibos con soporte para reintentos.
    
    El grafo implementa el siguiente flujo:
    1. Clasificar imagen → Validar clasificación
    2. Si es NO_VALIDO → Verificar intentos máximos
    3. Si no alcanzó el límite → Solicitar nueva imagen → Esperar imagen (INTERRUPCIÓN)
    4. Si llega nueva imagen → Volver a clasificar (loop)
    5. Si alcanzó límite → Terminar
    6. Si es válido → Extraer datos (TODO) → Terminar

    Returns:
        CompiledGraph: Grafo compilado con persistencia e interrupciones configuradas
    """
    log.info("[GRAPH] Creating receipt processing workflow")

    # Obtener dependencias del contenedor
    container = get_container()
    nodes = WorkFlowNodes(
        llm_service=container.instance_openai_service,
        wsp_service=container.wsp_service,
        image_service=container.storage_service,
        receipts_repository=container.receipt_repository
    )

    # Crear el grafo con el esquema de estado
    workflow = StateGraph(ReceiptState)

    # ===== AGREGAR NODOS =====
    log.info("[GRAPH] Adding nodes to workflow")
    workflow.add_node("classify_image_node", nodes.classify_image_node)
    workflow.add_node("decision_nodes_with_interrupt", nodes.decision_nodes_with_interrupt)
    workflow.add_node("data_extraction_node", nodes.data_extraction_node)
    workflow.add_node("upload_image_node", nodes.upload_image_node)
    workflow.add_node("persistence_data_node", nodes.persistence_data_node)
    workflow.add_node("send_confirmation_node", nodes.send_confirmation_node)
    workflow.add_node("max_intent_node", nodes.max_intent_node)
    workflow.add_node("max_intent_limit_node", nodes.max_intent_limit_node)
    workflow.add_node("end_node", nodes.end_node)

    # ===== DEFINIR FLUJO =====
    log.info("[GRAPH] Defining workflow edges")

    # Punto de inicio: Clasificar imagen
    workflow.add_edge(START, "classify_image_node")
    
    # - classify_image_node -> decision_nodes_with_interrupt | end_node
    # - decision_nodes_with_interrupt -> data_extraction_node | max_intent_limit_node | max_intent_node
    # - data_extraction_node -> upload_image_node
    # - upload_image_node -> persistence_data_node
    # - persistence_data_node -> send_confirmation_node
    # - send_confirmation_node -> end_node
    # - max_intent_node -> classify_image_node
    
    # Nodos finales que terminan el flujo
    workflow.add_edge("end_node", END)
    workflow.add_edge("max_intent_limit_node", END)
    
    # ===== COMPILAR CON PERSISTENCIA E INTERRUPCIONES =====
    log.info("[GRAPH] Compiling workflow with checkpointer and interruptions")
    
    compiled_graph = workflow.compile()
    
    log.info("[GRAPH] Workflow compiled successfully")
    return compiled_graph


# Instancia singleton del grafo compilado
_compiled_workflow = None


def get_workflow():
    """
    Obtiene la instancia singleton del grafo compilado.
    
    Returns:
        CompiledGraph: Grafo compilado listo para usar
    """
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = create_receipt_workflow()
    return _compiled_workflow
