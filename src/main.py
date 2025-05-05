import flet as ft
from views import home, inicio


def main(page: ft.Page):
    page.views.append(inicio.get_home_view(page))
    # Navigate directly to login page on startup
    page.go("/inicio")


ft.app(target=main)
