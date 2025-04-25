import flet as ft
from views import home


def main(page: ft.Page):
    page.views.append(home.get_home_view(page))
    # Navigate directly to login page on startup
    page.go("/home")


ft.app(target=main)
