import flet as ft
from views import trayecto, home

import time
def get_elegir_transporte_view(page: ft.Page) -> ft.View:
    page.title = "Elegir Transporte"

    # Container to hold the dynamic grid
    grid_container = ft.Column()

    # Transport options
    transport_options = [
        {"title": "En bus", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/bus_select_t.png", "key": "BUS%2CWALK"},
        {"title": "En tren", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/tren_select_t.png", "key": "TRAM%2CRAIL%2CSUBWAY%2CFUNICULAR%2CGONDOLA%2CWALK"},
        {"title": "Sólo a pie", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/a_pie_select_t.png", "key": "WALK"},
        {"title": "En taxi", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/taxi_select_t.png", "key": "CAR_PICKUP"},
        {"title": "En coche", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/taxi_select_t.png", "key": "driving-car"},
        {"title": "En bicicleta", "time": "xx min/h", "hour": "xx:xx", "icon": "src/assets/taxi_select_t.png",
         "key": "cycling-road"},
    ]

    # Create each transport button
    def create_button(option):
        container = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=option["icon"], width=40, height=40),
                    ft.Text(option["title"], weight="bold", size=16, text_align="center", color="black"),
                    ft.Text(f"Llegarás en {option['time']}", size=12, text_align="center", color="black"),
                    ft.Text(f"(a las {option['hour']})", size=12, text_align="center", color="black"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            width=140,
            height=140,
            bgcolor=ft.colors.LIGHT_BLUE_200,
            border_radius=10,
            padding=10,
            alignment=ft.alignment.center,
            on_click=lambda e: select_transport(e.control),
            on_tap_down=lambda e: on_press_down(e.control),
            #on_tap_up=lambda e: on_press_up(e.control),
            scale=ft.transform.Scale(scale=1),
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
        )

        def select_transport(control):
            page.client_storage.set("transporte", option["key"])
            page.views.append(trayecto.get_trayecto_view(page))
            page.go("/trayecto")


        def on_press_down(e):
            container.scale = 0.85
            page.update()
            time.sleep(0.2)
            container.scale = 1
            page.update()


        return container

    # Generate rows based on number of columns
    def build_buttons(columns: int):
        buttons = [create_button(opt) for opt in transport_options]
        rows = []
        for i in range(0, len(buttons), columns):
            row_items = buttons[i:i + columns]
            rows.append(
                ft.Row(
                    controls=row_items,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=min(10, page.width // 10),
                    wrap=False,
                )
            )
        return rows

    # Rebuild layout when resized
    def update_layout(e=None):
        columns = 1 if page.width < 400 else 2
        grid_container.controls = build_buttons(columns)
        page.update()

    def go_home():
        if page.views:
            page.views.pop()
        page.views.append(home.get_home_view(page))
        page.go("/home")

    page.on_resize = update_layout
    update_layout()

    # Return the composed view
    return ft.View(
        route="/elegir_transporte",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            # Header row
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.CircleAvatar(
                                                content=ft.Image(src="src/assets/bus_not_black.png",
                                                                 width=30,
                                                                 height=30,
                                                                 fit=ft.ImageFit.CONTAIN
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
                                        on_click=lambda e: go_home(),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=20, color="transparent"),
                            ft.Text(
                                "¿Cómo te gustaría ir?",
                                size=22,
                                weight="bold",
                                text_align="center",
                            ),
                            ft.Divider(height=10, color="transparent"),
                            grid_container,
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
