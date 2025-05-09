import flet as ft
from curl_cffi import requests

def get_trayecto_view(page: ft.Page) -> ft.View:
    page.title = "Tu Trayecto"
    url = "https://api.openrouteservice.org/v2/directions/"+page.client_storage.get("transporte")

    # Request headers
    headers = {
        "Authorization": "5b3ce3597851110001cf6248e9a9c74a263b4d3ab4e44745b333078c",
        "Content-Type": "application/json"
    }

    # Request body
    data = {
        "coordinates": [
            [-8.6286, 42.870],
            [-3.921433098110138, 40.43052641351046]
        ]
    }

    # Make the POST request
    trayecto = requests.post(url, headers=headers, json=data)

    # Print the response
    print("Status Code:", trayecto.status_code)
    return ft.View(
        route="/trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            # Header row with logo and back button
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.CircleAvatar(
                                                content=ft.Image(
                                                    src="src/assets/bus_not_black.png",
                                                    width=30,
                                                    height=30,
                                                    fit=ft.ImageFit.CONTAIN,
                                                ),
                                                bgcolor=ft.colors.LIGHT_BLUE_200,
                                            ),
                                            ft.Text("T.H.", size=20, weight="bold"),
                                        ],
                                        spacing=10,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK,
                                        icon_color=ft.colors.WHITE,
                                        bgcolor=ft.colors.DEEP_ORANGE,
                                        on_click=lambda e: page.go("/elegir_transporte"),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=20, color="transparent"),

                            # Title
                            ft.Text(
                                "Tu Trayecto",
                                size=24,
                                weight="bold",
                                text_align="center",
                            ),

                            ft.Divider(height=10, color="transparent"),

                            # Placeholder for trip summary content
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Resumen del trayecto", size=18, weight="bold", color=ft.colors.BLACK),
                                        ft.Text("• Medio:" + page.client_storage.get("transporte"), color=ft.colors.BLACK),
                                        ft.Text("• Hora de llegada: xx:xx", color=ft.colors.BLACK),
                                        # Optionally add a Map or route graphic
                                        ft.Container(
                                            height=200,
                                            bgcolor=ft.colors.GREY_200,
                                            border_radius=10,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("Mapa del trayecto (opcional)"),
                                        ),
                                    ],
                                    spacing=10
                                ),
                                padding=20,
                                bgcolor=ft.colors.LIGHT_BLUE_50,
                                border_radius=10,
                            ),
                        ],
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    alignment=ft.alignment.top_center,
                    expand=True,
                )
            )
        ]
    )
