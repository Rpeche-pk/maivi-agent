"""
Ejemplo de cómo manejar múltiples implementaciones de LlmService.
"""
from typing import Dict, Type, Optional
from llm.domain.llm_service import LlmService
from llm.infrastructure.openai_service import OpenAiService
# from llm.infrastructure.anthropic_service import AnthropicService  # Futuro
# from llm.infrastructure.gemini_service import GeminiService  # Futuro
from shared.config import settings


class LlmServiceFactory:
    """
    Factory para crear instancias de LlmService según el proveedor.
    
    Permite agregar nuevos proveedores sin modificar código existente.
    """
    
    # Registro de implementaciones disponibles
    _registry: Dict[str, Type[LlmService]] = {
        "openai": OpenAiService,
        # "anthropic": AnthropicService,  # Agregar cuando esté disponible
        # "gemini": GeminiService,  # Agregar cuando esté disponible
    }
    
    @classmethod
    def create(cls, provider: str) -> LlmService:
        """
        Crea una instancia de LlmService según el proveedor.
        
        Args:
            provider: Nombre del proveedor (openai, anthropic, gemini)
            
        Returns:
            LlmService: Instancia del servicio LLM
            
        Raises:
            ValueError: Si el proveedor no está registrado
        """
        service_class = cls._registry.get(provider.lower())
        
        if not service_class:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Disponibles: {available}"
            )
        
        return service_class()
    
    @classmethod
    def register(cls, name: str, service_class: Type[LlmService]):
        """
        Registra una nueva implementación de LlmService.
        
        Útil para agregar proveedores en runtime o desde plugins.
        """
        cls._registry[name.lower()] = service_class
    
    @classmethod
    def available_providers(cls) -> list[str]:
        """Retorna lista de proveedores disponibles."""
        return list(cls._registry.keys())


class MultiProviderContainer:
    """
    Contenedor que soporta múltiples proveedores de LLM.
    """
    
    _instance: Optional['MultiProviderContainer'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'MultiProviderContainer':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar contenedor."""
        if not MultiProviderContainer._initialized:
            # Caché de servicios por proveedor
            self._services: Dict[str, LlmService] = {}
            self._default_provider = "openai"  # Por defecto
            
            MultiProviderContainer._initialized = True
    
    @property
    def llm_service(self) -> LlmService:
        """
        Obtiene el servicio LLM por defecto.
        
        Returns:
            LlmService: Servicio según configuración o proveedor por defecto
        """
        # Intentar obtener de configuración
        provider = getattr(settings, 'LLM_PROVIDER', self._default_provider)
        return self.get_service(provider)
    
    def get_service(self, provider: str) -> LlmService:
        """
        Obtiene un servicio LLM específico (con caché).
        
        Args:
            provider: Nombre del proveedor
            
        Returns:
            LlmService: Instancia del servicio (Singleton por proveedor)
        """
        provider = provider.lower()
        
        if provider not in self._services:
            # Crear nueva instancia usando el factory
            self._services[provider] = LlmServiceFactory.create(provider)
        
        return self._services[provider]
    
    def set_default_provider(self, provider: str):
        """
        Establece el proveedor por defecto.
        
        Args:
            provider: Nombre del proveedor
        """
        # Validar que existe
        if provider.lower() not in LlmServiceFactory.available_providers():
            raise ValueError(f"Proveedor '{provider}' no disponible")
        
        self._default_provider = provider.lower()


# Función helper para obtener el contenedor
def get_multi_provider_container() -> MultiProviderContainer:
    """Obtiene instancia del contenedor multi-proveedor."""
    return MultiProviderContainer()


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def example_1_default_provider():
    """Ejemplo 1: Usar proveedor por defecto."""
    container = get_multi_provider_container()
    
    # Obtener servicio por defecto (openai)
    service = container.llm_service
    print(f"Servicio por defecto: {type(service).__name__}")


def example_2_specific_provider():
    """Ejemplo 2: Usar proveedor específico."""
    container = get_multi_provider_container()
    
    # Obtener servicio específico
    openai_service = container.get_service("openai")
    # anthropic_service = container.get_service("anthropic")  # Cuando esté disponible
    
    print(f"OpenAI Service: {type(openai_service).__name__}")


def example_3_change_default():
    """Ejemplo 3: Cambiar proveedor por defecto."""
    container = get_multi_provider_container()
    
    # Cambiar proveedor por defecto
    # container.set_default_provider("anthropic")  # Cuando esté disponible
    
    # Ahora llm_service retornará Anthropic
    service = container.llm_service
    print(f"Nuevo servicio por defecto: {type(service).__name__}")


def example_4_singleton_per_provider():
    """Ejemplo 4: Verificar Singleton por proveedor."""
    container = get_multi_provider_container()
    
    # Obtener el mismo proveedor varias veces
    service1 = container.get_service("openai")
    service2 = container.get_service("openai")
    
    # Deben ser la misma instancia
    assert service1 is service2
    print(f"✓ Singleton por proveedor verificado: {id(service1) == id(service2)}")


def example_5_available_providers():
    """Ejemplo 5: Listar proveedores disponibles."""
    providers = LlmServiceFactory.available_providers()
    print(f"Proveedores disponibles: {', '.join(providers)}")


if __name__ == "__main__":
    print("=" * 60)
    print("MÚLTIPLES IMPLEMENTACIONES - EJEMPLOS")
    print("=" * 60)
    
    print("\n[1] Proveedor por defecto")
    example_1_default_provider()
    
    print("\n[2] Proveedor específico")
    example_2_specific_provider()
    
    print("\n[3] Cambiar proveedor por defecto")
    example_3_change_default()
    
    print("\n[4] Singleton por proveedor")
    example_4_singleton_per_provider()
    
    print("\n[5] Proveedores disponibles")
    example_5_available_providers()
    
    print("\n" + "=" * 60)
