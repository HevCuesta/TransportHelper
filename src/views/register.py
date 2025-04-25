import flet as ft

def get_register_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Register"


    username = ft.TextFileld (
        username = "Usuario",
        border = ft.InputBorder.OUTLINE,
        prefix_icon = ft.icons.PERSON
    )

    email = ft.TextFileld (
        label = "correo",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.EMAIL
    )

    