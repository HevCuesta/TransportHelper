from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from db import DatabaseService

@dataclass
class Usuario:
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    email: Optional[str] = None
    fecha_creacion: Optional[str] = None
    
    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'Usuario':
        """Crear una instancia de Usuario desde un diccionario."""
        return cls(
            id=datos.get("id"),
            username=datos.get("username", ""),
            password=datos.get("password", ""),
            email=datos.get("email"),
            fecha_creacion=datos.get("created_at")
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convertir Usuario a representación de diccionario."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "created_at": self.fecha_creacion
        }


@dataclass
class PreferenciasUsuario:
    """Modelo de preferencias de usuario para almacenar configuraciones específicas del usuario."""
    id_usuario: int
    tema: str = "light"
    rutas_favoritas: Optional[str] = None
    ultimo_inicio_sesion: Optional[str] = None
    
    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'PreferenciasUsuario':
        """Crear una instancia de PreferenciasUsuario desde un diccionario."""
        return cls(
            id_usuario=datos["user_id"],
            tema=datos.get("theme", "light"),
            rutas_favoritas=datos.get("favorite_routes"),
            ultimo_inicio_sesion=datos.get("last_login")
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convertir PreferenciasUsuario a representación de diccionario."""
        return {
            "user_id": self.id_usuario,
            "theme": self.tema,
            "favorite_routes": self.rutas_favoritas,
            "last_login": self.ultimo_inicio_sesion
        }


@dataclass
class UbicacionGuardada:
    """Modelo para ubicaciones guardadas por el usuario."""
    id: Optional[int] = None
    id_usuario: int = 0
    nombre: str = ""
    direccion: str = ""
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    es_favorito: bool = False
    
    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'UbicacionGuardada':
        """Crear una instancia de UbicacionGuardada desde un diccionario."""
        return cls(
            id=datos.get("id"),
            id_usuario=datos.get("user_id", 0),
            nombre=datos.get("name", ""),
            direccion=datos.get("address", ""),
            latitud=datos.get("latitude"),
            longitud=datos.get("longitude"),
            es_favorito=bool(datos.get("is_favorite", False))
        )
    
    def a_dict(self) -> Dict[str, Any]:
        """Convertir UbicacionGuardada a representación de diccionario."""
        return {
            "id": self.id,
            "user_id": self.id_usuario,
            "name": self.nombre,
            "address": self.direccion,
            "latitude": self.latitud,
            "longitude": self.longitud,
            "is_favorite": self.es_favorito
        }


class RepositorioUsuario:
    """Repositorio para operaciones de base de datos relacionadas con usuarios."""
    
    def __init__(self, servicio_db=None):
        """Inicializar con un servicio de base de datos opcional."""
        self.db = servicio_db or DatabaseService()
    
    def crear_usuario(self, usuario: Usuario) -> int:
        """Crear un nuevo usuario en la base de datos."""
        return self.db.create_user(
            username=usuario.username,
            password=usuario.password,
            email=usuario.email
        )
    
    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        """Obtener un usuario por su nombre de usuario."""
        datos_usuario = self.db.get_user_by_username(username)
        if not datos_usuario:
            return None
        return Usuario.desde_dict(datos_usuario)
    
    def actualizar_preferencias(self, preferencias: PreferenciasUsuario) -> bool:
        """Actualizar las preferencias de un usuario."""
        return self.db.update_user_preferences(
            user_id=preferencias.id_usuario,
            theme=preferencias.tema,
            favorite_routes=preferencias.rutas_favoritas
        )
    
    def actualizar_timestamp_inicio_sesion(self, id_usuario: int) -> bool:
        """Actualizar la marca de tiempo del último inicio de sesión de un usuario."""
        return self.db.update_login_timestamp(id_usuario)


class RepositorioUbicacion:
    """Repositorio para operaciones de base de datos relacionadas con ubicaciones."""
    
    def __init__(self, servicio_db=None):
        """Inicializar con un servicio de base de datos opcional."""
        self.db = servicio_db or DatabaseService()
    
    def agregar_ubicacion(self, ubicacion: UbicacionGuardada) -> int:
        """Agregar una nueva ubicación guardada."""
        return self.db.add_location(
            user_id=ubicacion.id_usuario,
            name=ubicacion.nombre,
            address=ubicacion.direccion,
            latitude=ubicacion.latitud,
            longitude=ubicacion.longitud,
            is_favorite=ubicacion.es_favorito
        )
    
    def obtener_ubicaciones_usuario(self, id_usuario: int, solo_favoritos: bool = False) -> List[UbicacionGuardada]:
        """Obtener todas las ubicaciones guardadas de un usuario."""
        datos_ubicaciones = self.db.get_user_locations(
            user_id=id_usuario,
            favorites_only=solo_favoritos
        )
        return [UbicacionGuardada.desde_dict(ubic) for ubic in datos_ubicaciones]
