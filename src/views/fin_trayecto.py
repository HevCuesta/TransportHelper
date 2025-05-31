import flet as ft
from flet.core.types import PagePlatform
from views import inicio
import warnings
warnings.filterwarnings("ignore")

# Store URLs
play_store_url = "https://play.google.com/store/apps/details?id=com.playstack.balatro.android"
app_store_url = "https://apps.apple.com/es/app/balatro/id6502451661"
pc_url = "https://store.steampowered.com/app/2379780/Balatro/"

# Platform-based store selection
tienda_url = ""
if ft.PagePlatform == PagePlatform.IOS:
    tienda_url = app_store_url
elif ft.PagePlatform == PagePlatform.ANDROID:
    tienda_url = play_store_url
else:
    tienda_url = pc_url


def get_fin_trayecto_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper - Fin del trayecto"

    # Dialog to confirm redirection to app store
    valorar_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Valorar aplicación"),
        content=ft.Text("Serás redirigido a la tienda de aplicaciones"),
        actions=[
            ft.TextButton(
                "Ok",
                on_click=lambda e: (
                    page.launch_url(tienda_url),
                    page.close(valorar_dialog),
                    page.views.append(inicio.get_home_view(page)),
                    page.go("/inicio")
                ),
                adaptive=True
            ),
            ft.TextButton(
                "No",
                on_click=lambda e: (
                    page.close(valorar_dialog),
                    page.views.append(inicio.get_home_view(page)),
                    page.go("/inicio")
                ),
                adaptive=True
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        adaptive=True,
    )

    # Main navigation button logic
    def go_home(e):
        if page.views:
            page.views.clear()
        page.go("/home")

    # Buttons
    boton_si_valora = ft.ElevatedButton(
        "Sí",
        on_click=lambda e: page.open(valorar_dialog),
        adaptive=True
    )
    boton_no_valora = ft.ElevatedButton(
        "No",
        on_click=lambda e: (
            page.views.append(inicio.get_home_view(page)),
            page.go("/inicio")
        ),
        adaptive=True
    )

    return ft.View(
        route="/fin_trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Image(
                                src="src/assets/estrella_fin.png",
                                width=150,
                                height=150,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Image(
                                src="src/assets/bus_black.png" if page.theme_mode == ft.ThemeMode.DARK else "src/assets/bus_not_black.png",
                                width=150,
                                height=150,
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            ft.Text("🎉 ¡Felicidades!", size=20, weight="bold", text_align="center"),
                            ft.Text("Has llegado a tu destino.", size=12, text_align="center"),
                            ft.Divider(height=10, color="transparent"),
                            ft.Text("¿Nos das tu opinión sobre el viaje?", size=20, weight=ft.FontWeight.BOLD, text_align="center"),
                            ft.Row(
                                [boton_si_valora, boton_no_valora],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=10, color="transparent"),
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
                        spacing=15,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=30
                )
            )
        ]
    )
