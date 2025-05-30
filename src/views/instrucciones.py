import flet as ft
from views import ayuda
import json

def get_instrucciones_view(page: ft.Page) -> ft.View:
    def go_home():
        if page.views:
            page.views.pop()
            page.views.append(ayuda.get_ayuda_view(page))
        page.go("/ayuda")

    page.title = "Resolución de problemas"
    view = ft.View(route="/instrucciones", padding=20)

    # Load data
    with open("src/assets/instrucciones.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    key = page.client_storage.get("problema")
    instrucciones = next((d for d in data if d["key"] == key), None)

    if not instrucciones:
        view.controls.append(ft.Text("No se encontraron instrucciones para este problema."))
        return view

    textos = instrucciones["text"]
    imagenes = instrucciones["images"]  # Ahora será un array
    
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

    def update_content():
        content_text.value = textos[index.value]
        img = imagenes[index.value]
        
        if img == "phone":
            image_container.content = ft.Icon(ft.icons.PHONE, size=100, color=ft.colors.GREEN)
        else:
            image_container.content = ft.Image(src=img, fit=ft.ImageFit.CONTAIN, width=200)
        
        prev_button.visible = index.value > 0
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

    def on_cancel(e):
        page.go("/")  # Or your desired route

    def on_resuelto(e):
        print("Problema resuelto")
        page.go("/")  # Or redirect elsewhere

    prev_button = ft.ElevatedButton("Atrás", icon=ft.icons.ARROW_BACK, on_click=on_prev, visible=False)
    next_button = ft.ElevatedButton("Siguiente", icon=ft.icons.ARROW_FORWARD, on_click=on_next)

    view.controls.extend([
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
        ft.Text("Siga las siguientes instrucciones y consejos para solucionar el problema", text_align=ft.TextAlign.CENTER, size=16),
        content_text,
        image_container,
        ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.ElevatedButton("He podido arreglar el problema", on_click=on_resuelto, bgcolor=ft.colors.GREEN_700, width=page.width * 0.9)
    ])

    update_content()
    return view