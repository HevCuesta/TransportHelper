import flet as ft
from flet_map import Map, Marker, MapLatitudeLongitude, TileLayer, MarkerLayer, MapInteractionConfiguration, MapInteractiveFlag
from views import login, register
from db import DatabaseService
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def get_home_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Inicio"
    
    db_service = DatabaseService()
    db_service.initialize_database()

    # Initialize geocoder
    geolocator = Nominatim(user_agent="transport_helper")

    # Coordenadas iniciales (Móstoles, Madrid)
    latitude = 40.37261
    longitude = -3.92162
    zoom = 15

    # Crear la capa de tiles (mapa base)
    tile_layer = TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    
    # Crear el marcador inicial
    marker = Marker(
        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.colors.RED, size=30),
        coordinates=MapLatitudeLongitude(latitude, longitude),
    )
    
    # Crear la capa de marcadores
    marker_layer = MarkerLayer(markers=[marker])

    # Crear el widget del mapa
    map_widget = Map(
        initial_center=MapLatitudeLongitude(latitude, longitude),
        initial_zoom=zoom,
        interaction_configuration=MapInteractionConfiguration(
            flags=MapInteractiveFlag.ALL
        ),
        height=None,
        width=None,
        expand=True,
        layers=[tile_layer, marker_layer],
    )

    location_entry = ft.TextField(
        label="Buscar ubicación",
        hint_text="Ingresa una dirección o lugar",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        border_radius=10
    )
    
    def update_map(lat, lng, new_zoom=None):
        # Actualizar el marcador existente en lugar de crear uno nuevo
        if marker_layer.markers and len(marker_layer.markers) > 0:
            marker_layer.markers[0].coordinates = MapLatitudeLongitude(lat, lng)
        
        # Si no hay marcador, crear uno nuevo
        else:
            new_marker = Marker(
                content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.colors.RED, size=30),
                coordinates=MapLatitudeLongitude(lat, lng),
            )
            marker_layer.markers = [new_marker]
        
        # Mover el centro del mapa
        if new_zoom is not None:
            map_widget.move_to(MapLatitudeLongitude(lat, lng), new_zoom)
        else:
            map_widget.move_to(MapLatitudeLongitude(lat, lng), map_widget.zoom)
        
        # Actualizar la página
        page.update()

    def search_location(e):
        if not location_entry.value:
            return
            
        try:
            # Usar Nominatim para geocodificar la dirección
            location = geolocator.geocode(location_entry.value, timeout=10)
            
            if location:
                # Si se encuentra la ubicación con Nominatim
                lat, lng = location.latitude, location.longitude
                update_map(lat, lng, zoom)
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Ubicación encontrada: {location.address}"),
                    action="OK"
                )
            else:
                # Fallback a ciudades predefinidas
                term = location_entry.value.lower()
                if "madrid" in term:
                    lat, lng = 40.4168, -3.7038
                elif "barcelona" in term:
                    lat, lng = 41.3851, 2.1734
                elif "valencia" in term:
                    lat, lng = 39.4699, -0.3763
                elif "sevilla" in term:
                    lat, lng = 37.3886, -5.9953
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("No se pudo encontrar la ubicación"),
                        action="OK"
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                update_map(lat, lng, 12)  # Zoom más alejado para ciudades
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Mostrando: {location_entry.value}"),
                    action="OK"
                )
            
            page.snack_bar.open = True
            page.update()
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error de geocodificación: {str(e)}"),
                action="OK"
            )
            page.snack_bar.open = True
            page.update()

    def login_click(e):
        page.views.append(login.get_login_view(page))
        page.go("/login")

    def registro_click(e):
        page.views.append(register.get_register_view(page))
        page.go("/register")

    return ft.View(
        "/inicio",
        controls=[
            ft.SafeArea(
                ft.Container(
                    ft.Column(
                        [
                            ft.Row([
                                ft.Text("TransportHelper", size=24, weight=ft.FontWeight.BOLD),
                            ], alignment=ft.MainAxisAlignment.CENTER),

                            ft.Row([
                                location_entry,
                                ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    on_click=search_location,
                                    tooltip="Buscar ubicación"
                                )
                            ]),

                            ft.Container(
                                content=map_widget,
                                border_radius=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                margin=ft.margin.only(top=10, bottom=10, right=10),
                                padding=0,
                                expand=True,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            ),

                            ft.Text("Selecciona una ubicación en el mapa", size=14),
                        ],
                        spacing=20,
                        expand=True
                    ),
                    padding=20,
                    expand=True
                ),
                expand=True
            )
        ]
    )