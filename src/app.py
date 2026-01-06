"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
from IPython.display import Image, display
from maivi_agent.application.graph import get_workflow


def print_image_node():
    compiled_graph = get_workflow()
    
    display(Image(compiled_graph.get_graph(xray=True).draw_mermaid_png()))

if __name__ == "__main__":
    print_image_node()
