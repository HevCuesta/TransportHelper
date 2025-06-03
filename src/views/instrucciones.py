import flet as ft
from views import ayuda, home, inicio
import json


def get_instrucciones_view(page: ft.Page) -> ft.View:
    def go_to_ayuda(e):
        if page.views:
            page.views.pop()
        page.go("/ayuda")

    def go_home():
        if page.views:
            page.views.clear()
            page.views.append(inicio.get_home_view(page)),
        page.go("/inicio")

    page.title = "Resolución de problemas"

    # Load data
    with open("src/assets/instrucciones.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    key = page.client_storage.get("problema")
    instrucciones = next((d for d in data if d["key"] == key), None)

    if not instrucciones:
        return ft.View(
            route="/instrucciones",
            controls=[
                ft.Text("No se encontraron instrucciones para este problema.")
            ],
            padding=20,
        )

    textos = instrucciones["text"]
    imagenes = instrucciones["images"]

    index = ft.Ref[int]()
    index.value = 0

    content_text = ft.Text(value=textos[0], text_align=ft.TextAlign.CENTER, size=16)

    image_container = ft.Container(
        content=None,
        alignment=ft.alignment.center,
        height=250,
        width=250,
        bgcolor=ft.colors.GREY_300,
        border_radius=10,
        margin=20
    )

    prev_button = ft.ElevatedButton("Atrás", icon=ft.icons.ARROW_BACK, visible=False)
    next_button = ft.ElevatedButton("Siguiente", icon=ft.icons.ARROW_FORWARD)
    volver_ayuda_button = ft.ElevatedButton(
        "Volver a ayuda",
        icon=ft.icons.ARROW_BACK,
        on_click=go_to_ayuda,
        visible=False
    )

    def update_content():
        content_text.value = textos[index.value]
        img = imagenes[index.value]

        if img == "phone":
            image_container.content = ft.Icon(ft.icons.PHONE, size=100, color=ft.colors.GREEN)
        else:
            image_container.content = ft.Image(src=img, fit=ft.ImageFit.CONTAIN, width=200)

        prev_button.visible = index.value > 0
        volver_ayuda_button.visible = index.value == 0
        next_button.visible = index.value < len(textos) - 1

        page.update()

    def on_next(e):
        if index.value < len(textos) - 1:
            index.value += 1
            update_content()

    def on_prev(e):
        if index.value > 0:
            index.value -= 1
            update_content()

    def on_resuelto(e):
        print("Problema resuelto")
        if page.views:
            page.views.pop()
            page.views.pop()
        page.go("/trayecto")

    prev_button.on_click = on_prev
    next_button.on_click = on_next

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

    update_content()

    return ft.View(
        route="/instrucciones",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column(
                        [
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
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=10, color="transparent"),
                            ft.Text(
                                "Siga las siguientes instrucciones y consejos para solucionar el problema",
                                text_align=ft.TextAlign.CENTER,
                                size=16
                            ),
                            ft.Divider(height=10, color="transparent"),
                            content_text,
                            image_container,
                            ft.Row(
                                [volver_ayuda_button, prev_button, next_button],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            dialog_cancel_trip,
                            ft.ElevatedButton(
                                "He podido arreglar el problema",
                                on_click=on_resuelto,
                                bgcolor="#005d00",
                                width=page.width * 0.9
                            ),
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
