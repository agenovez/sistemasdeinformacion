import unittest
import datetime
from unittest.mock import Mock, call
from .interfaces import InstalacionDTO, IRepositorioInstalaciones, IPublicadorEventos
from .core_module import InstalacionManager

# -- Implementaciones Falsas (Fakes) para Inyección de Dependencias --
# Estos objetos simulan el comportamiento de la BD y el Bus de Eventos.

class FakeRepositorioInstalaciones(IRepositorioInstalaciones):
    """Simula la Base de Datos para que el módulo sea testeable."""
    def __init__(self, agenda_inicial: List[Dict[str, Any]] = None):
        self.instalaciones = agenda_inicial if agenda_inicial is not None else []
        self._next_id = 1
        
    def guardar(self, datos: InstalacionDTO) -> int:
        # Simula guardar en la BD
        self.instalaciones.append({"id": self._next_id, "datos": datos})
        new_id = self._next_id
        self._next_id += 1
        return new_id
        
    def consultar_agenda(self, fecha: datetime.date) -> List[Dict[str, Any]]:
        # Simula consultar la BD
        return [
            {"tecnico_id": 101, "fecha": fecha, "direccion": "Ocupada 1"},
            {"tecnico_id": 102, "fecha": fecha, "direccion": "Ocupada 2"},
        ]

# -- Clase de Prueba (Testability) --

class InstalacionManagerTest(unittest.TestCase):

    def setUp(self):
        # 1. Setup de dependencias simuladas (Arrange)
        self.mock_repositorio = FakeRepositorioInstalaciones()
        self.mock_publicador = Mock(IPublicadorEventos) # Mocking para verificar la llamada asíncrona
        
        # 2. Instancia del SUT (System Under Test) con inyección de Fakes
        self.manager = InstalacionManager(self.mock_repositorio, self.mock_publicador)

        # 3. Datos de prueba válidos para el futuro
        self.fecha_futura = datetime.date.today() + datetime.timedelta(days=7)
        self.datos_validos = InstalacionDTO(
            cliente_id=1, 
            fecha=self.fecha_futura, 
            tecnico_id=999, # Técnico 999 está disponible en FakeRepositorio
            direccion="Calle Falsa 123"
        )

    # TEST: Funcionalidad Principal OK
    def test_agendar_instalacion_exitosa(self):
        # Act
        instalacion_id = self.manager.agendar_instalacion(self.datos_validos)
        
        # Assert (Validación Funcional y de Efectos Secundarios)
        self.assertIsInstance(instalacion_id, int)
        self.assertEqual(len(self.mock_repositorio.instalaciones), 1, "Debe haber una instalación guardada")
        
        # Verificar que se llamó al publicador (Notificación Asíncrona)
        self.mock_publicador.publicar.assert_called_once()
        self.mock_publicador.publicar.assert_called_with('instalacion_agendada', Any)
        
    # TEST: Validación de Seguridad/Consistencia (Fechas pasadas)
    def test_validar_fecha_pasada(self):
        datos_pasados = InstalacionDTO(1, datetime.date.today() - datetime.timedelta(days=1), 999, "Pasado")
        
        # Assert (Verificar que el ValueError se levanta - Sanitización de Negocio)
        with self.assertRaisesRegex(ValueError, "futura"):
            self.manager.agendar_instalacion(datos_pasados)

    # TEST: Regla de Negocio (Disponibilidad)
    def test_verificar_disponibilidad_ocupada(self):
        # Intentar agendar con un técnico OCUPADO (IDs 101 o 102 en el FakeRepo)
        datos_ocupados = InstalacionDTO(1, self.fecha_futura, 101, "Ocupada")
        
        # Assert (Verificar que el PermissionError se levanta)
        with self.assertRaisesRegex(PermissionError, "disponible"):
            self.manager.agendar_instalacion(datos_ocupados)

if __name__ == '__main__':
    unittest.main()
