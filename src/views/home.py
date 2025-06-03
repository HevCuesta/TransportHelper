import flet as ft
from views import inicio
from db import DatabaseService

def get_home_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Inicio"
    
    db_service = DatabaseService()
    db_service.initialize_database()

    def home_click(e):
        page.views.append(inicio.get_home_view(page))
        # Navigate directly to login page on startup
        page.go("/inicio")

    return ft.View(
        "/home",
        controls=[
            ft.SafeArea(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text("TransportHelper", size=30, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=20, color="transparent"),
                            ft.GestureDetector(
                                on_tap=home_click,
                                content=ft.Image(
                                    src="src/assets/bus_black.png" if page.theme_mode == ft.ThemeMode.DARK else "src/assets/bus_not_black.png",
                                    width=150,
                                    height=150,
                                    fit=ft.ImageFit.CONTAIN
                                )
                            ),
                            ft.Divider(height=40, color="transparent"),
                            ft.ElevatedButton(
                                "Viajar en transporte público", 
                                on_click=home_click,
                                width=320,
                                height=50,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            ),
                            ft.Divider(height=20, color="transparent"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                ),
                expand=True,
            )
        ]
    )
