import flet as ft
from views import login, register
from db import DatabaseService

def get_home_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Inicio"
    
    db_service = DatabaseService()
    db_service.initialize_database()

    # Location search field
    location_entry = ft.TextField(
        label="Buscar ubicación",
        hint_text="Ingresa una dirección o lugar",
        prefix_icon=ft.icons.SEARCH,
        expand=True,
        border_radius=10
    )
    
    # Map component using Flet's WebView to load a map service
    map_view = ft.WebView(
        src="https://www.openstreetmap.org/export/embed.html?bbox=-74.2,4.5,-74.0,4.8&layer=mapnik",
        height=400,
        width=800,
        expand=True
    )
    
    # For demonstrating map location selection
    def search_location(e):
        if location_entry.value:
            # In a real implementation, you'd call a geocoding API here
            # and update the map coordinates based on the search result
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Buscando: {location_entry.value}"),
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
                            
                            # Location search bar
                            ft.Row([
                                location_entry,
                                ft.IconButton(
                                    icon=ft.icons.SEARCH,
                                    on_click=search_location,
                                    tooltip="Buscar ubicación"
                                )
                            ]),
                            
                            # Map component
                            ft.Container(
                                content=map_view,
                                border_radius=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                margin=ft.margin.only(top=10, bottom=10),
                                padding=5
                            ),
                            
                            ft.Text("Selecciona una ubicación en el mapa", size=14),
                            
                            # Bottom navigation options
                            ft.Row([
                                ft.ElevatedButton(
                                    "Iniciar Sesión", 
                                    on_click=login_click,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    )
                                ),
                                ft.ElevatedButton(
                                    "Registro", 
                                    on_click=registro_click,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    )
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                        ],
                        spacing=20,
                    ),
                    padding=20,
                    expand=True
                ),
                expand=True
            )
        ]
    )
