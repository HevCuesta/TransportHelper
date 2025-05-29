import flet as ft
from views import debug


def main(page: ft.Page):
    page.views.append(debug.get_debug_view(page))
    page.go("/debug")


ft.app(target=main)
