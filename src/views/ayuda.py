import flet as ft
from . import instrucciones, home, inicio

import time
def get_ayuda_view(page: ft.Page) -> ft.View:
    page.title = "¿Qué problema ha surgido?"

    # Container to hold the dynamic grid
    grid_container = ft.Column()

    # Ayudas
    ayudas = [
        {"title": "No puedo pagar el transporte actual", "icon": "src/assets/no_puedo_pagar.png", "key": "no-puedo-pagar"},
        {"title": "No sé a dónde ir ahora", "icon": "src/assets/no_se_donde_ir.png", "key": "no-se-donde-ir"},
        {"title": "He perdido el transporte que tenía que coger", "icon": "src/assets/transporte_perdido.png", "key": "transporte-perdido"},
        {"title": "Me he saltado la parada", "icon": "src/assets/parada_pasada.png", "key": "parada-pasada"},
        {"title": "He perdido algo", "icon": "src/assets/algo_perdido.png", "key": "algo-perdido"},
        {"title": "Me sucedió otra cosa", "icon": "src/assets/sucedio_otra_cosa.png","key": "sucedio-otra-cosa"},
    ]

    # Create each transport button
    def create_button(option):
        container = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=option["icon"], width=65, height=65),
                    ft.Text(option["title"], weight="bold", size=14, text_align="center", color="black"),
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
            on_click=lambda e: select_ayuda(e.control),
            on_tap_down=lambda e: on_press_down(e.control),
            scale=ft.transform.Scale(scale=1),
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
        )

        def select_ayuda(control):
            page.client_storage.set("problema", option["key"])
            page.views.append(instrucciones.get_instrucciones_view(page))
            page.go("/instrucciones")


        def on_press_down(e):
            container.scale = 0.85
            page.update()
            time.sleep(0.2)
            container.scale = 1
            page.update()


        return container

    # Generate rows based on number of columns
    def build_buttons(columns: int):
        buttons = [create_button(opt) for opt in ayudas]
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

    def go_home():
        if page.views:
            page.views.clear()
            page.views.append(inicio.get_home_view(page)),
        page.go("/inicio")
    def update_layout(e=None):
        columns = 1 if page.width < 400 else 2
        grid_container.controls = build_buttons(columns)
        page.update()

    def on_resuelto(e):
        print("Problema resuelto")
        if page.views:
            page.views.pop()
            page.go("/trayecto")

    confirm_cancel_dialog = ft.Ref()

    dialog_cancel_trip = ft.AlertDialog(
        ref=confirm_cancel_dialog,
        modal=True,
        title=ft.Text("¿Cancelar trayecto?"),
        content=ft.Text("¿Estás seguro de que quieres cancelar el trayecto actual?"),
        actions=[
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_color=ft.colors.RED,
                on_click=lambda e: (setattr(confirm_cancel_dialog.current, "open", False), page.update())
            ),
            ft.IconButton(
                icon=ft.icons.CHECK,
                icon_color=ft.colors.GREEN,
                on_click=lambda e: go_home()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    def show_confirm_cancel_dialog(e):
        confirm_cancel_dialog.current.open = True
        page.update()



    page.on_resize = update_layout
    update_layout()

    # Return the composed view
    return ft.View(
        route="/ayuda",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
                            # Header row
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK,
                                        icon_color=ft.colors.WHITE,
                                        bgcolor=ft.colors.DEEP_ORANGE,
                                        on_click=show_confirm_cancel_dialog,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.GestureDetector(
                                                on_tap=show_confirm_cancel_dialog,
                                                content=ft.CircleAvatar(
                                                    content=ft.Image(
                                                        src="src/assets/bus_not_black.png",
                                                        width=30,
                                                        height=30,
                                                        fit=ft.ImageFit.CONTAIN,
                                                    ),
                                                    bgcolor=ft.colors.LIGHT_BLUE_200,
                                                ),
                                            ),
                                            ft.Text("T.H.", size=20, weight="bold"),
                                        ],
                                        spacing=10,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=10, color="transparent"),
                            ft.Text(
                                "¿Qué te ha sucedido?",
                                size=22,
                                weight="bold",
                                text_align="center",
                            ),
                            ft.Divider(height=10, color="transparent"),
                            grid_container,
                            dialog_cancel_trip,
                            ft.ElevatedButton("He podido arreglar el problema", on_click=on_resuelto, bgcolor="#005d00",
                                              width=page.width * 0.9)

                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    padding=20,
                    alignment=ft.alignment.top_center,
                    expand=True,
                )
            )
        ]
    )
