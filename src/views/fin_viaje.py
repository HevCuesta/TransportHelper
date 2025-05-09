import flet as ft
from flet.core.types import PagePlatform
from views import inicio

play_store_url="https://play.google.com/store/apps/details?id=com.playstack.balatro.android"
app_store_url="https://apps.apple.com/es/app/balatro/id6502451661"
pc_url="https://store.steampowered.com/app/2379780/Balatro/"
tienda_url=""
if ft.PagePlatform == PagePlatform.IOS:
    tienda_url=app_store_url
elif ft.PagePlatform == PagePlatform.ANDROID:
    tienda_url=play_store_url
else:
    tienda_url=pc_url



def get_fin_viaje_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Fin del viaje"

    # Modal dialog definition
    te_vas_pa_la_playstore_jimbo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Valorar aplicación"),
        content=ft.Text("Serás redirigido a la tienda de aplicaciones"),
        actions=[
            ft.TextButton("Ok", on_click=lambda e: (page.launch_url(tienda_url), page.close(te_vas_pa_la_playstore_jimbo)), adaptive=True),
            ft.TextButton("No", on_click=lambda e: (page.close(te_vas_pa_la_playstore_jimbo),page.views.append(inicio.get_home_view(page)),page.go("/inicio")),adaptive=True),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        adaptive=True,
    )

    boton_si_valora = ft.ElevatedButton(
        "Si",
        on_click=lambda e: (page.open(te_vas_pa_la_playstore_jimbo),page.views.append(inicio.get_home_view(page)),page.go("/inicio")),
        adaptive=True
    )
    boton_no_valora = ft.ElevatedButton("No",on_click=lambda e: (page.views.append(inicio.get_home_view(page)),page.go("/inicio")),adaptive=True)

    # Return view
    return ft.View(
        "/finviaje",
        controls=[
            ft.SafeArea(
                ft.Container(
                    ft.Column(
                        [
                            ft.Image(
                                src="src/assets/bus_black.png" if page.theme_mode == ft.ThemeMode.DARK else "src/assets/bus_not_black.png",
                                width=150,
                                height=150,
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            ft.Image(src="src/assets/estrella_fin.svg",width=150,height=150,fit=ft.ImageFit.CONTAIN),
                            ft.Divider(height=20, color="transparent"),
                            ft.Text("Nos das tu opinión sobre el viaje?", size=30, weight=ft.FontWeight.BOLD),
                            boton_si_valora,
                            boton_no_valora,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                ),
                expand=True,
            )
        ]
    )
