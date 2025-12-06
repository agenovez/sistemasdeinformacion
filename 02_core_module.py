import datetime
from typing import List, Dict, Any
from .interfaces import IRepositorioInstalaciones, IPublicadorEventos, InstalacionDTO

class InstalacionManager:
    """
    Gestiona la lógica de negocio (CORE) del agendamiento y asignación de instalaciones.
    Aplica Cohesión Alta y Responsabilidad Única.
    """
    
    # -- Inyección de Dependencias (Dependency Inversion / Testability) --
    # Las dependencias se reciben, no se crean aquí.
    def __init__(self, repositorio: IRepositorioInstalaciones, publicador: IPublicadorEventos):
        self.repositorio = repositorio
        self.publicador = publicador

    # -- B. Métodos de Validación y Seguridad (Sanitización) --
    def validar_datos(self, datos: InstalacionDTO):
        """Aplica validaciones de Clean Code y Seguridad (Sanitización básica / Consistencia)."""
        
        # 1. Validación Básica de Sanitización (Evita nulos o inyecciones simples)
        if not all([datos.cliente_id, datos.fecha, datos.tecnico_id, datos.direccion]):
            raise ValueError("Todos los campos obligatorios deben estar presentes y ser válidos.")
        
        # 2. Validación de Consistencia de Negocio (Fechas futuras)
        if datos.fecha < datetime.date.today():
            # Error de negocio: no se puede agendar en el pasado.
            raise ValueError("La fecha de agendamiento debe ser futura.")

    # -- C. Regla de Negocio Cohesiva (Funcionalidad Principal) --
    def verificar_disponibilidad(self, tecnico_id: int, fecha: datetime.date) -> bool:
        """
        Verifica si el técnico ya tiene una instalación agendada en la fecha dada.
        (Lógica de Negocio).
        """
        # Esta lógica es simple: asume que una entrada en la agenda para ese día significa OCUPADO.
        agenda_del_dia = self.repositorio.consultar_agenda(fecha)
        
        for item in agenda_del_dia:
            if item.get('tecnico_id') == tecnico_id:
                return False
        return True

    # -- A. Flujo de Control Principal (Función Corta) --
    def agendar_instalacion(self, datos: InstalacionDTO) -> int:
        """
        Flujo para agendar: valida, verifica disponibilidad, guarda y notifica.
        """
        self.validar_datos(datos) # 1. Validación/Sanitización

        # 2. Validación de Regla de Negocio
        if not self.verificar_disponibilidad(datos.tecnico_id, datos.fecha):
            raise PermissionError(f"Técnico {datos.tecnico_id} no está disponible el {datos.fecha}.")

        # 3. Persistencia (Delegación a I/O - Accidental Complexity)
        instalacion_id = self.repositorio.guardar(datos)
        
        # 4. Notificación Asíncrona (Delegación a otro Servicio)
        evento_datos = {"instalacion_id": instalacion_id, "fecha": str(datos.fecha), "tecnico": datos.tecnico_id}
        self.publicador.publicar("instalacion_agendada", evento_datos)
        
        return instalacion_id

    # -- E. Lógica Adicional (Ejemplo para Reprogramación) --
    def reprogramar_instalacion(self, instalacion_id: int, nueva_fecha: datetime.date):
        """
        Maneja la lógica de negocio para la reprogramación (simplificado).
        """
        if nueva_fecha < datetime.date.today():
            raise ValueError("La nueva fecha debe ser futura.")

        # Lógica de reprogramación...
        # ...
        
        # Publica evento de reprogramación
        evento_datos = {"instalacion_id": instalacion_id, "fecha_anterior": "2025-01-01", "nueva_fecha": str(nueva_fecha)}
        self.publicador.publicar("instalacion_reprogramada", evento_datos)
        
        return True
