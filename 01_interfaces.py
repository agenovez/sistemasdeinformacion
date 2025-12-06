import datetime
from typing import List, Dict, Any, Protocol

# DTOs (Data Transfer Objects) para tipado claro y validación de entrada
class InstalacionDTO:
    """Define la estructura mínima de datos de entrada para una instalación."""
    def __init__(self, cliente_id: int, fecha: datetime.date, tecnico_id: int, direccion: str):
        self.cliente_id = cliente_id
        self.fecha = fecha
        self.tecnico_id = tecnico_id
        self.direccion = direccion

# Interfaz de Contrato (Patrón Repository / Dependency Inversion)
class IRepositorioInstalaciones(Protocol):
    """Contrato que el Servicio de Persistencia (E) debe implementar."""
    def guardar(self, datos: InstalacionDTO) -> int:
        """Persiste la instalación y retorna su ID."""
        ...
        
    def consultar_agenda(self, fecha: datetime.date) -> List[Dict[str, Any]]:
        """Consulta la agenda para verificar la disponibilidad."""
        ...

# Interfaz de Contrato para Eventos (Bus de Eventos / Servicio D)
class IPublicadorEventos(Protocol):
    """Contrato para publicar eventos de notificación (asíncrono)."""
    def publicar(self, evento: str, datos: Dict[str, Any]):
        """Envía el evento al bus/cola sin esperar respuesta."""
        ...
