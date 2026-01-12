"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
from IPython.display import Image, display
from maivi_agent.application.graph import get_workflow


def save_graph_image():
    """Guarda la imagen del grafo en un archivo PNG."""
    compiled_graph = get_workflow()
    
    # Generar la imagen PNG
    png_bytes = compiled_graph.get_graph(xray=True).draw_mermaid_png()
    
    # Guardar en archivo
    with open("graph_workflow.png", "wb") as f:
        f.write(png_bytes)
    
    print("✅ Imagen del grafo guardada en: graph_workflow.png")
    
    # Opcional: También mostrar en Jupyter/IPython
    display(Image(png_bytes))



if __name__ == "__main__":
    save_graph_image()
