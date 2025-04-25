import flet as ft
from views import login


def main(page: ft.Page):
    page.views.append(login.get_login_view(page))
    # Navigate directly to login page on startup
    page.go("/login")


ft.app(target=main)
