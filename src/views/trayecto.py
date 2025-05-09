import flet as ft
from curl_cffi import requests
from views import elegir_transporte

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
    route_data = requests.post(url, headers=headers, json=data).json()
    instructions = []
    instruction_text = "No instructions available"
    current_step_index = 1
    try:
        steps = route_data["routes"][0]["segments"][0]["steps"]
        instruction_text = ft.Ref()
    except Exception as e:
        instructions.append(ft.Text("Error al cargar instrucciones.", color=ft.colors.RED))
    def go_to_elegir_transporte():
        if page.views:
            page.views.pop()
        page.views.append((elegir_transporte.get_elegir_transporte_view(page)))
        page.go("/elegir_transporte")

    def update_instruction():
        step = steps[current_step_index]
        instruction_text.current.value = f"{current_step_index + 1}/{len(steps)}: {step['instruction']}"
        page.update()

    def next_step(e):
        nonlocal current_step_index
        if current_step_index < len(steps) - 1:
            current_step_index += 1
            update_instruction()

    def previous_step(e):
        nonlocal current_step_index
        if current_step_index > 0:
            current_step_index -= 1
            update_instruction()


    return ft.View(
        route="/trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
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
                                        on_click=lambda e: go_to_elegir_transporte(),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=20, color="transparent"),
                            ft.Text("Tu Trayecto", size=24, weight="bold", text_align="center"),
                            ft.Divider(height=10, color="transparent"),

                            # Summary Box
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Resumen del trayecto", size=18, weight="bold", color=ft.colors.BLACK),
                                        ft.Text("• Medio: " + page.client_storage.get("transporte"),
                                                color=ft.colors.BLACK),
                                        ft.Text("• Hora de llegada: xx:xx", color=ft.colors.BLACK),
                                        ft.Container(
                                            height=200,
                                            bgcolor=ft.colors.GREY_200,
                                            border_radius=10,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("Mapa del trayecto (opcional)", color=ft.colors.BLACK),
                                        ),
                                    ],
                                    spacing=10
                                ),
                                padding=20,
                                bgcolor=ft.colors.LIGHT_BLUE_50,
                                border_radius=10,
                            ),

                            # Instructions Box
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Instrucción actual:", size=18, weight="bold"),
                                        ft.Text("", ref=instruction_text, color=ft.colors.BLACK),
                                        ft.Row(
                                            controls=[
                                                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=previous_step),
                                                ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=next_step),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                    ],
                                spacing=5),
                                padding=15,
                                bgcolor=ft.colors.GREY_100,
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