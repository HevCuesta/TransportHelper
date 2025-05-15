import flet as ft
from views import home, debug


def main(page: ft.Page):
    page.views.append(debug.get_debug_view(page))
    # Navigate directly to login page on startup
    page.go("/debug")


ft.app(target=main)
