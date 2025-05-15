import flet as ft
from flet_map import Map, Marker, MapLatitudeLongitude, TileLayer, MarkerLayer, MapInteractionConfiguration, MapInteractiveFlag
from db import DatabaseService # Asumo que la tienes
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import requests
import time
import traceback # Para imprimir trazas de error completas

# ... (DatabaseService y otras importaciones/configuraciones iniciales) ...

def get_home_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Inicio"
    
    # ... (inicialización de db_service, geolocator, coordenadas, capas del mapa, marcador, map_widget) ...
    # TU CÓDIGO DE INICIALIZACIÓN AQUÍ (lo he omitido por brevedad, pero debe estar)
    # Ejemplo de inicializaciones necesarias para el contexto:
    db_service = DatabaseService()
    db_service.initialize_database()
    geolocator = Nominatim(user_agent="transport_helper_app_v2") # User agent único
    latitude = 40.37261
    longitude = -3.92162
    initial_zoom = 15 # Renombrado para claridad

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
    )
    suggestions_container = ft.Container(
        content=ft.Column([], tight=True),
        visible=False,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        border=ft.border.all(1, ft.colors.BLACK),
        padding=10,
        width=300, # O el ancho del location_entry
        shadow=ft.BoxShadow(
            spread_radius=1, blur_radius=15, color=ft.colors.BLACK54, offset=ft.Offset(0, 5),
        ),
        # Ajustar posición si es necesario, por ejemplo, usando Stack
    )
    location_entry = ft.TextField(
        label="Buscar ubicación",
        hint_text="Ingresa una dirección o lugar",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        border_radius=10,
        # on_change se definirá más abajo para usar get_suggestions
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
        
        map_widget.move_to(MapLatitudeLongitude(lat, lng), current_map_zoom)

    def update_map(lat, lng, new_zoom=None, perform_page_update=True):
        """Actualiza el mapa y opcionalmente la página."""
        try:
            _prepare_map_update(lat, lng, new_zoom)
            if perform_page_update:
                page.update()
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                print("Ignorando error de event loop cerrado en update_map")
            else:
                print(f"Error en update_map: {e}")
                traceback.print_exc()
        except Exception as ex:
            print(f"Error inesperado en update_map: {ex}")
            traceback.print_exc()


    # get_location_suggestions_sync DEBE ESTAR DEFINIDA AQUÍ O IMPORTADA
    # Esta es tu función original que usa `requests.get`
    def get_location_suggestions_sync(query):
        try:
            params = {
                'q': query, 'format': 'json', 'addressdetails': 1, 'limit': 5, 'accept-language': 'es'
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
            return []
        except Exception as e:
            print(f"Error procesando sugerencias: {e}")
            traceback.print_exc()
            return []

    def fetch_suggestions_thread_worker(query: str):
        """Hilo de trabajo para obtener sugerencias y actualizar UI."""
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
        
        suggestions_container.content.controls = suggestion_controls
        suggestions_container.visible = bool(suggestion_controls)
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

    def get_suggestions(e: ft.ControlEvent): # e.data es el texto del TextField
        """Manejador para on_change del TextField, inicia la obtención de sugerencias."""
        query = e.data
        nonlocal last_query_details # Usar el diccionario
        current_time = time.time()

        if not query or len(query) < 3:
            if suggestions_container.visible:
                suggestions_container.visible = False
                try: page.update()
                except Exception as ex_update: print(f"Error ocultando sugerencias: {ex_update}")
            return

        # Debounce: no buscar si la misma query se hizo hace < 0.5s
        if query == last_query_details["text"] and (current_time - last_query_details["time"] < 0.5):
            return
        
        # Throttle: Si es una nueva query, pero la última fue hace muy poco, también esperar un poco
        # Esto es más complejo; el debounce anterior es el más simple y efectivo aquí.
        # Considera `page.debounce` si Flet lo ofrece directamente para on_change.

        last_query_details["text"] = query
        last_query_details["time"] = current_time
        
        print(f"Iniciando búsqueda de sugerencias para: '{query}'")
        page.run_thread(handler=lambda: fetch_suggestions_thread_worker(query))

    location_entry.on_change = get_suggestions # Asignar después de definir get_suggestions

    def search_location_thread_worker(search_term: str):
        """Hilo de trabajo para geocodificar y actualizar mapa/UI."""
        lat, lng, display_message, new_zoom_level, error_message = None, None, None, initial_zoom, None

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
            if lat is not None and lng is not None:
                _prepare_map_update(lat, lng, new_zoom_level) # Prepara cambios sin actualizar
                if display_message:
                    page.snack_bar = ft.SnackBar(ft.Text(display_message), open=True)
            elif error_message:
                page.snack_bar = ft.SnackBar(ft.Text(error_message), open=True)
            
            suggestions_container.visible = False # Ocultar siempre las sugerencias
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
        tooltip="Buscar ubicación"
    )

    # --- Estructura de la Vista ---
    search_section = ft.Column(
        [
            ft.Row([location_entry, search_button], alignment=ft.MainAxisAlignment.START),
            ft.Stack([ # Usar Stack para superponer el contenedor de sugerencias
                suggestions_container 
            ]) 
            # Alternativamente, si suggestions_container no necesita superponerse exactamente
            # bajo el TextField sino simplemente aparecer debajo:
            # suggestions_container 
        ],
        spacing=0, # O un valor pequeño si es necesario
        tight=True, # Si quieres que la columna se ajuste a su contenido
        # alignment=ft.MainAxisAlignment.START, # Opcional
        # horizontal_alignment=ft.CrossAxisAlignment.START # Opcional
    )

    return ft.View(
        "/inicio",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("TransportHelper", size=24, weight=ft.FontWeight.BOLD),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            search_section,
                            ft.Container(
                                content=map_widget,
                                border_radius=10,
                                border=ft.border.all(1, ft.colors.OUTLINE), # ft.colors.OUTLINE_VARIANT puede ser más sutil
                                margin=ft.margin.only(top=10), # Ajustar márgenes
                                # padding=0, # El mapa no suele necesitar padding
                                expand=True, # Importante para que el mapa llene el espacio
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            ),
                            # ft.Text("Selecciona una ubicación en el mapa", size=14), # Puede ser redundante o confuso
                        ],
                        # spacing=15, # Espaciado entre elementos principales
                        expand=True # La columna principal debe expandirse
                    ),
                    padding=15, # Padding general del contenedor principal
                    expand=True # El contenedor principal debe expandirse
                ),
                expand=True # SafeArea debe expandirse
            )
        ],
        # vertical_alignment=ft.MainAxisAlignment.START, # Para que el contenido empiece arriba
        # horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Para que los elementos se estiren horizontalmente si pueden
    )
