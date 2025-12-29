# LLM Module - Gestión de Dependencias

## Estructura del Módulo

```
src/llm/
├── application/
│   └── llm_orchestrator.py      # Orquestador principal
├── domain/
│   ├── llm_client.py            # Interface cliente LLM
│   ├── llm_entities.py          # Entidades del dominio
│   ├── llm_exceptions.py        # Excepciones personalizadas
│   └── llm_service.py           # Interface servicio LLM
└── infrastructure/
    ├── dependency_container.py   # ⭐ Contenedor de dependencias
    ├── openai_client.py         # Implementación OpenAI client
    └── openai_service.py        # Implementación OpenAI service
```

## Dependency Container - Gestor de Dependencias

### ¿Qué es?

El `DependencyContainer` es un **gestor centralizado** que utiliza el patrón **Singleton** para:

- ✅ Crear y gestionar todas las dependencias del módulo LLM
- ✅ Garantizar una única instancia de cada servicio (Singleton)
- ✅ Inyectar automáticamente las dependencias necesarias
- ✅ Facilitar el testing y mantenimiento del código

### Patrón Singleton Implementado

```python
class DependencyContainer:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Beneficios:**
- Una única instancia en toda la aplicación
- Reutilización eficiente de recursos
- Estado consistente y predecible
- Fácil acceso desde cualquier parte del código

### Grafo de Dependencias

```
┌─────────────────────────┐
│  DependencyContainer    │ (Singleton)
└───────────┬─────────────┘
            │
            ├──► OpenAIClient (Singleton)
            │
            ├──► OpenAiService (Singleton)
            │      └──► usa OpenAIClient
            │
            └──► LlmOrchestrator (Singleton)
                   └──► usa LlmService (OpenAiService)
```

### Uso Rápido

#### 1. Importar

```python
from llm.infrastructure import get_container
```

#### 2. Obtener dependencias

```python
# Obtener el contenedor (Singleton)
container = get_container()

# Opción 1: Acceder al orquestador directamente
orchestrator = container.llm_orchestrator

# Opción 2: Acceder a servicios específicos
llm_service = container.llm_service
openai_client = container.openai_client
```

#### 3. Ejecutar operaciones

```python
from llm.domain.llm_entities import LLMRequestConfig, UserInputType

# Configurar solicitud
request = LLMRequestConfig(
    input_type=UserInputType.TEXT,
    prompt="Mi prompt",
    temperature=0.0
)

# Ejecutar
chain = await orchestrator.execute_llm(request)
result = await chain.ainvoke({"message_user": "Hola"})
```

## Ejemplos Completos

### Ejemplo 1: Clasificación Simple

```python
import asyncio
from llm.infrastructure import get_container
from llm.domain.llm_entities import LLMRequestConfig, UserInputType

async def main():
    container = get_container()
    orchestrator = container.llm_orchestrator
    
    config = LLMRequestConfig(
        input_type=UserInputType.TEXT,
        prompt="Clasificar recibo",
        temperature=0.0
    )
    
    chain = await orchestrator.execute_llm(config)
    result = await chain.ainvoke({
        "message_user": "Recibo de ElectroDunas"
    })
    
    print(result)

asyncio.run(main())
```

### Ejemplo 2: Con Imagen (Multimodal)

```python
import base64
from llm.infrastructure import get_container
from llm.domain.llm_entities import LLMRequestConfig, UserInputType

async def classify_image(image_path: str):
    # Cargar imagen
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    # Configurar
    container = get_container()
    config = LLMRequestConfig(
        input_type=UserInputType.IMAGE,
        prompt="Clasificar recibo",
        temperature=0.0
    )
    
    # Ejecutar
    chain = await container.llm_orchestrator.execute_llm(config)
    result = await chain.ainvoke({
        "system_content": "Eres Maivi",
        "text_content": "Clasifica como LUZ, AGUA o GAS",
        "message_user": image_b64
    })
    
    return result
```

### Ejemplo 3: Salida Estructurada

```python
from pydantic import BaseModel
from llm.infrastructure import get_container
from llm.domain.llm_entities import LLMRequestConfig, UserInputType

class ReciboInfo(BaseModel):
    tipo: str
    empresa: str
    monto: float

async def extract_info():
    config = LLMRequestConfig(
        input_type=UserInputType.TEXT,
        prompt="Extraer información",
        structured_output=ReciboInfo,
        temperature=0.0
    )
    
    container = get_container()
    chain = await container.llm_orchestrator.execute_llm(config)
    
    result = await chain.ainvoke({
        "message_user": "Recibo ElectroDunas por 218 soles"
    })
    
    print(f"Tipo: {result.tipo}")
    print(f"Empresa: {result.empresa}")
    print(f"Monto: {result.monto}")
```

## Testing

### Resetear entre tests

```python
import pytest
from llm.infrastructure import DependencyContainer

@pytest.fixture(autouse=True)
def reset_dependencies():
    yield
    DependencyContainer.reset_singleton()
```

### Verificar Singleton

```python
def test_singleton():
    from llm.infrastructure import get_container
    
    c1 = get_container()
    c2 = get_container()
    
    assert c1 is c2  # ✓ Misma instancia
```

## Archivos de Referencia

- **Contenedor**: [dependency_container.py](src/llm/infrastructure/dependency_container.py)
- **Ejemplos**: [dependency_container_usage.py](examples/dependency_container_usage.py)
- **Tests**: [test_dependency_container.py](tests/test_dependency_container.py)
- **Documentación**: [DEPENDENCY_CONTAINER.md](docs/DEPENDENCY_CONTAINER.md)

## Ventajas del Diseño

| Ventaja | Descripción |
|---------|-------------|
| **Desacoplamiento** | Los componentes no conocen cómo crear sus dependencias |
| **Testabilidad** | Fácil mockear servicios para pruebas unitarias |
| **Mantenibilidad** | Cambios centralizados en un solo lugar |
| **Reutilización** | Instancias compartidas evitan duplicación |
| **Escalabilidad** | Agregar nuevos servicios sin modificar código existente |

## Configuración

Crear archivo `.env`:

```env
OPEN_AI_KEY=sk-...
MODEL_NAME=gpt-4o-mini
NAME_AGENT=Maivi
```

## Ejecutar Ejemplos

```bash
# Ejemplo básico en main.py
python main.py

# Ejemplos completos
python examples/dependency_container_usage.py

# Tests (si pytest está instalado)
pytest tests/test_dependency_container.py -v
```
