import flet as ft
from flet_map import Map, Marker, MapLatitudeLongitude, TileLayer, MarkerLayer, MapInteractionConfiguration, MapInteractiveFlag, PolylineLayer, PolylineMarker
import requests
import polyline

def get_ruta_view(page: ft.Page):
    page.title = "OTP Ruta en Mapa"
    page.scroll = "AUTO"
    
    # Contenedor principal para retornar
    main_container = ft.Column([])
    
    # Llamar a OTP
    from_lat, from_lon = 40.4168, -3.7038  # Madrid
    to_lat, to_lon = 40.4531, -3.6880  # Madrid Norte
    
    # Crear las cadenas para la API
    from_place = f"{from_lat},{from_lon}"
    to_place = f"{to_lat},{to_lon}"
    
    url = "http://otp.danielcuesta.es/otp/routers/default/plan"
    params = {
        "fromPlace": from_place,
        "toPlace": to_place,
        "mode": "WALK,BUS,SUBWAY,RAIL",
        "date": "2025-05-16",
        "time": "09:00am",
        "numItineraries": 2
    }
    
    # Mostrar un spinner mientras cargamos los datos
    progress = ft.ProgressRing()
    main_container.controls.append(progress)
    
    try:
        resp = requests.get(url, params=params)
        print(resp.url)
        if resp.status_code != 200:
            raise Exception("Error al obtener datos de OTP")
        data = resp.json()
        print(data)
        legs = data["plan"]["itineraries"][0]["legs"]
        
        # Crear las capas base del mapa
        tile_layer = TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
        
        # Crear marcadores para inicio y fin
        start_marker = Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.GREEN, size=30),
            coordinates=MapLatitudeLongitude(from_lat, from_lon)
        )
        
        end_marker = Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=30),
            coordinates=MapLatitudeLongitude(to_lat, to_lon)
        )
        
        marker_layer = MarkerLayer(markers=[start_marker, end_marker])
        
        # Crear las polilíneas para cada tramo del viaje
        polylines = []
        
        for leg in legs:
            coords = polyline.decode(leg["legGeometry"]["points"])
            
            # Determinar el color según el modo de transporte
            color = ft.Colors.BLUE
            if "mode" in leg:
                if leg["mode"] == "WALK":
                    color = ft.Colors.GREEN
                elif leg["mode"] == "BUS":
                    color = ft.Colors.RED
                elif leg["mode"] == "SUBWAY" or leg["mode"] == "RAIL":
                    color = ft.Colors.ORANGE
            
            # Crear la polilínea para este tramo
            poly = PolylineMarker(
                coordinates=[MapLatitudeLongitude(lat, lon) for lat, lon in coords],
                border_stroke_width=0.8,
                color=color
            )
            polylines.append(poly)
        
        # Crear el mapa
        mapa = Map(
            initial_center=MapLatitudeLongitude((from_lat + to_lat) / 2, (from_lon + to_lon) / 2),
            initial_zoom=13,
            interaction_configuration=MapInteractionConfiguration(flags=MapInteractiveFlag.ALL),
            width=page.width,
            height=400,
            layers=[tile_layer, marker_layer, PolylineLayer(polylines=polylines)],
            min_zoom=10
        )

        # Mostrar información del viaje
        duration = data["plan"]["itineraries"][0]["duration"]
        duration_minutes = int(duration / 60)
        
        trip_info = ft.Column([
            ft.Text(f"Duración total: {duration_minutes} minutos", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Tramos del viaje:", size=16, weight=ft.FontWeight.BOLD),
        ])
        
        for i, leg in enumerate(legs):
            mode = leg.get("mode", "DESCONOCIDO")
            leg_duration = int(leg.get("duration", 0) / 60)
            from_name = leg.get("from", {}).get("name", "Origen")
            to_name = leg.get("to", {}).get("name", "Destino")
            
            trip_info.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Tramo {i+1}: {mode}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"De: {from_name}"),
                        ft.Text(f"A: {to_name}"),
                        ft.Text(f"Duración: {leg_duration} minutos"),
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=5,
                    margin=ft.margin.only(bottom=10)
                )
            )
        
        # Crear la vista con el mapa y la información
        main_container.controls.clear()
        main_container.controls.extend([
            ft.Text("Ruta de transporte público", size=24, weight=ft.FontWeight.BOLD),
            mapa,
            trip_info
        ])
        
    except Exception as e:
        # En caso de error, mostrar un mensaje
        main_container.controls.clear()
        main_container.controls.extend([
            ft.Text("Error al cargar la ruta", color=ft.Colors.RED),
            ft.Text(str(e))
        ])
    
    return main_container