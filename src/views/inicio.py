import flet as ft
from flet_map import Map, Marker, MapLatitudeLongitude, TileLayer, MarkerLayer, MapInteractionConfiguration, MapInteractiveFlag
from db import DatabaseService 
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import requests
import time
import traceback
from views import elegir_transporte
import geocoder
g = geocoder.ip('me')
curr_lat, curr_lng = g.latlng

# ... (DatabaseService y otras importaciones/configuraciones iniciales) ...

def get_home_view(page: ft.Page) -> ft.View:
    lat, lng = None, None
    page.title = "TransportHelper Inicio"
    db_service = DatabaseService()
    db_service.initialize_database()
    geolocator = Nominatim(user_agent="transport_helper_app_v2") # User agent único
    latitude = curr_lat
    longitude = curr_lng
    initial_zoom = 15 #Renombrado para claridad

    tile_layer = TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    marker = Marker(
        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.colors.RED, size=30),
        coordinates=MapLatitudeLongitude(latitude, longitude),
    )
    marker_layer = MarkerLayer(markers=[marker])
    map_widget = Map(
        initial_center=MapLatitudeLongitude(latitude, longitude),
        initial_zoom=initial_zoom,
        interaction_configuration=MapInteractionConfiguration(flags=MapInteractiveFlag.ALL),
        expand=True, # Generalmente True si está en un Container que expande
        layers=[tile_layer, marker_layer],
        min_zoom=10
    )

    warning_text = ft.Text(
        value="",
        color=ft.colors.RED,
        size=14,
        text_align="center",
        visible=False
    )
    def go_to_elegir_transporte(e):
        """Navega a la vista de trayecto."""
        nonlocal lat, lng
        if lat and lng:
            page.views.append(elegir_transporte.get_elegir_transporte_view(page))
            page.client_storage.set("dest_lat", lat)
            page.client_storage.set("dest_lng", lng)
            page.go("/elegir_transporte")
        else:
            warning_text.visible = True
            warning_text.value = "Elige una ubicación de las que ofrecemos antes de continuar"
            page.update()
        
    ir_aqui_button = ft.ElevatedButton(
        text="Ir Aquí",
        icon=ft.icons.DIRECTIONS,
        on_click=go_to_elegir_transporte,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
        ),
        width=200,
    )
    location_entry = ft.TextField(
        label="Busca aquí a donde quieres ir",
        hint_text="Ingresa una dirección o lugar",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        border_radius=10,
        border_width=4,
        border_color="#C0E9FF" if page.theme_mode == ft.ThemeMode.DARK else "#C0E9FF",
        label_style=ft.TextStyle(color="#C0E9FF" if page.theme_mode == ft.ThemeMode.DARK else "#63B3ED"),
        focused_border_color="#1A365D"
        #hint_style=ft.TextStyle(color=ft.colors.BLACK)
        
        # on_change se definirá más abajo para usar get_suggestions
    )
    suggestions_container = ft.Container(
        content=ft.Column([], tight=True),
        visible=False,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        border=ft.border.all(1, ft.colors.BLACK),
        padding=10,
        expand=True,
        width=location_entry.width, 
        shadow=ft.BoxShadow(
            spread_radius=1, blur_radius=15, color=ft.colors.BLACK54, offset=ft.Offset(0, 5),
        ),
    )
    # FIN DE INICIALIZACIONES DE EJEMPLO

    # --- Funciones de Lógica y UI ---

    def _prepare_map_update(lat, lng, new_zoom=None):
        """Prepara los cambios en el mapa sin llamar a page.update()."""
        current_map_zoom = map_widget.zoom if new_zoom is None else new_zoom
        
        if marker_layer.markers:
            marker_layer.markers[0].coordinates = MapLatitudeLongitude(lat, lng)
        else:
            new_marker = Marker(
                content=ft.Icon(ft.icons.LOCATION_ON, color=ft.colors.RED, size=30),
                coordinates=MapLatitudeLongitude(lat, lng),
            )
            marker_layer.markers = [new_marker] # Reemplaza la lista de marcadores
        
        map_widget.move_to(
            MapLatitudeLongitude(lat, lng), 
            current_map_zoom,
            animation_curve=ft.AnimationCurve(ft.AnimationCurve.EASE),  # Smooth animation curve
            animation_duration=ft.Duration(seconds=3),       # Animation duration in milliseconds
        )


    def get_location_suggestions_sync(query):
        """Obtiene sugerencias de ubicación con restricción de país.
        
        Args:
            query: Consulta de búsqueda
            country_codes: Lista de códigos ISO de países separados por coma (default: "es" para España)
        """
        suggestions_container.visible = True
        try:
             
            # Define a bounding box around Madrid
            # Format: min_lon,min_lat,max_lon,max_lat (roughly covers Madrid region)
            madrid_viewbox = "-4.6,39.6,-2.9,41.2"
            
            params = {
            'q': query, 
            'format': 'json', 
            'addressdetails': 1, 
            'limit': 5, 
            'accept-language': 'es',
            'countrycodes': 'es',  # Restricción de país
            'viewbox': madrid_viewbox,  # Restricción a Madrid y alrededores
            'bounded': 1  # Fuerza que los resultados estén dentro del viewbox
            }
            headers = {'User-Agent': 'TransportHelper/1.0 (Python Requests)'} # User agent específico
            response = requests.get(
            'https://nominatim.openstreetmap.org/search', params=params, headers=headers, timeout=10
            )
            response.raise_for_status() # Lanza error para códigos 4xx/5xx
            data = response.json()
            suggestions = []
            for item in data:
                address_parts = []
                if 'name' in item and item['name']: address_parts.append(item['name'])
                address = item.get('address', {})
                if 'road' in address:
                    road_name = address['road']
                    if 'house_number' in address: road_name += f" {address['house_number']}"
                    address_parts.append(road_name)
                for key in ['city', 'town', 'village', 'suburb', 'state', 'country']:
                    if key in address and address[key] not in address_parts:
                        address_parts.append(address[key])
                formatted_address = ", ".join(address_parts[:3])
                if formatted_address: suggestions.append(formatted_address)
            return suggestions
        except requests.exceptions.RequestException as e: # Captura errores de red/HTTP
            print(f"Error en la API de Nominatim (sugerencias): {e}")
            suggestions_container.visible = False
            return []
        except Exception as e:
            print(f"Error procesando sugerencias: {e}")
            suggestions_container.visible = False
            traceback.print_exc()
            return []

    def fetch_suggestions_thread_worker(query: str):
        """Hilo de trabajo para obtener sugerencias y actualizar UI."""
        suggestions_container.visible = True
        results = get_location_suggestions_sync(query) # Llamada bloqueante
        
        suggestion_controls = []
        if results:
            for address_text in results:
                suggestion_controls.append(
                    ft.TextButton(
                        text=address_text,
                        on_click=lambda _, addr=address_text: on_suggestion_click(addr),
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(10), # Usar ft.padding
                            # alignment=ft.alignment.center_left, # Predeterminado para TextButton
                        ),
                        # expand=True # Puede causar problemas de layout en Column vertical, ajustar según sea necesario
                    )
                )
        else:
            suggestion_controls.append(
                ft.Text("No se encontraron resultados. Pruebe dentro de Madrid, o una búsqueda más general.", size=12, color=ft.colors.RED)
            )
        
        suggestions_container.content.controls = suggestion_controls
        suggestions_container.visible = True
        # Ajustar altura dinámicamente o dejarla fija si causa problemas
        # suggestions_container.height = min(200, len(results) * 40) if results else 0 

        try:
            page.update()
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                print(f"Ignorando error de event loop cerrado en fetch_suggestions_thread_worker para query: {query}")
            else:
                print(f"Error en fetch_suggestions_thread_worker al actualizar UI: {e}")
                traceback.print_exc()
        except Exception as ex:
            print(f"Error inesperado en fetch_suggestions_thread_worker: {ex}")
            traceback.print_exc()

    last_query_details = {"text": "", "time": 0}

    def get_suggestions(e: ft.ControlEvent):
        """Manejador para on_submit del TextField, inicia la obtención de sugerencias."""
        query = e.data
        nonlocal last_query_details # Usar el diccionario
        current_time = time.time()

        if not query or len(query) < 3:
            if suggestions_container.visible:
                suggestions_container.visible = False
                try: page.update()
                except Exception as ex_update: print(f"Error ocultando sugerencias: {ex_update}")
            return

        # Throttle: Limitar la frecuencia de solicitudes a una por segundo (1000ms)
        time_since_last_request = current_time - last_query_details["time"]
        if time_since_last_request < 1.0:  # Si ha pasado menos de 1 segundo
            print(f"Throttling request for '{query}', too soon after previous request")
            return

        last_query_details["text"] = query
        last_query_details["time"] = current_time
        
        print(f"Iniciando búsqueda de sugerencias para: '{query}'")
        page.run_thread(handler=lambda: fetch_suggestions_thread_worker(query))

    # Asignar el evento on_submit en vez de on_change
    location_entry.on_submit = get_suggestions

    def search_location_thread_worker(search_term: str):
        nonlocal lat, lng
        """Hilo de trabajo para geocodificar y actualizar mapa/UI."""
        display_message, new_zoom_level, error_message = None, initial_zoom, None

        try:
            location = geolocator.geocode(search_term, timeout=10) # Bloqueante
            if location:
                lat, lng = location.latitude, location.longitude
                display_message = f"Ubicación: {location.address}"
            else: # Fallback
                term_lower = search_term.lower()
                # ... (tu lógica de fallback para Madrid, Barcelona, etc.)
                if "madrid" in term_lower: lat, lng, display_message, new_zoom_level = 40.4168, -3.7038, f"Mostrando: Madrid", 12
                elif "barcelona" in term_lower: lat, lng, display_message, new_zoom_level = 41.3851, 2.1734, f"Mostrando: Barcelona", 12
                # Añade más ciudades si es necesario
                else:
                    error_message = "Ubicación no encontrada por geocodificador ni en fallbacks."

        except (GeocoderTimedOut, GeocoderUnavailable) as geo_err:
            error_message = f"Error de geocodificación: {str(geo_err)}"
        except Exception as ex:
            error_message = f"Error inesperado buscando '{search_term}': {str(ex)}"
            print(error_message)
            traceback.print_exc()

        # Actualizar UI desde el hilo
        try:
            # Asegurarse de que el contenedor de sugerencias esté oculto
            suggestions_container.visible = False
            
            if lat is not None and lng is not None:
                _prepare_map_update(lat, lng, new_zoom_level) # Prepara cambios sin actualizar
                if display_message:
                    page.snack_bar = ft.SnackBar(ft.Text(display_message), open=True)
            elif error_message:
                page.snack_bar = ft.SnackBar(ft.Text(error_message), open=True)
            
            page.update() # Aplicar todos los cambios a la UI (mapa, snackbar, sugerencias)

        except RuntimeError as e_runtime:
            if "Event loop is closed" in str(e_runtime):
                print(f"Ignorando error (event loop cerrado) en search_location_thread_worker para: {search_term}")
            else:
                print(f"Error de Runtime en search_location_thread_worker: {e_runtime}")
                traceback.print_exc()
        except Exception as e_final:
            print(f"Error finalizando search_location_thread_worker: {e_final}")
            traceback.print_exc()



    def search_location(address_to_search=None):
        """Inicia la búsqueda de una ubicación en un hilo."""
        search_term = address_to_search if address_to_search else location_entry.value
        if not search_term:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingresa una ubicación."), open=True)
            try: page.update()
            except Exception as e: print(f"Error en snackbar (search_location): {e}")
            return
        
        print(f"Iniciando geocodificación para: '{search_term}'")
        page.run_thread(handler=lambda: search_location_thread_worker(search_term))

    def on_suggestion_click(selected_address: str):
        """Manejador para clic en una sugerencia."""
        suggestions_container.visible = True 
        location_entry.value = selected_address
        # No es necesario ocultar suggestions_container aquí, search_location_thread_worker lo hará.
        # El page.update() inmediato es para que el usuario vea el TextField actualizado.
        try:
            page.update() 
        except RuntimeError as e:
            if "Event loop is closed" in str(e): print("Ignorando error (on_suggestion_click - pre-search update)")
            else: print(f"Error actualizando UI en on_suggestion_click: {e}")
        except Exception as ex:
            print(f"Error inesperado en on_suggestion_click (pre-search): {ex}")

        search_location(selected_address) # Inicia la búsqueda con la dirección seleccionada


    search_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        on_click=lambda _: search_location(),
        tooltip="Buscar ubicación",
    )
    

    # Agregar margen superior al suggestions_container para colocarlo un poco más abajo
    suggestions_container.margin = ft.margin.only(top=120,left=40)
    page.overlay.append(suggestions_container)
    
    return ft.View(
        "/inicio",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [ft.Text("TransportHelper", size=24, weight=ft.FontWeight.BOLD)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row([location_entry, search_button], alignment=ft.MainAxisAlignment.START),
                            map_widget,
                            warning_text,
                            ft.Row(
                                [
                                    ir_aqui_button,
                                    
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        expand=True,
                    ),
                    padding=15,
                    expand=True,
                ),
                expand=True,
            )
        ],
    )
