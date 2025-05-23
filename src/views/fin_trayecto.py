import flet as ft
from curl_cffi import requests
from views import elegir_transporte
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import json

def get_fin_trayeto_view(page: ft.Page) -> ft.View:
    def go_home(e):
        if page.views:
            page.views.pop()
            page.views.pop()
            page.views.pop()
        page.go("/home")

    return ft.View(
        route="/fin_trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Text("🎉 ¡Felicidades!", size=32, weight="bold", text_align="center"),
                            ft.Text("Has llegado a tu destino.", size=20, text_align="center"),
                            ft.ElevatedButton(
                                text="Volver al menú principal",
                                bgcolor=ft.colors.DEEP_ORANGE,
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                ),
                                on_click=go_home
                            ),
                        ],
                        spacing=30,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30
                )
            )
        ]
    )
