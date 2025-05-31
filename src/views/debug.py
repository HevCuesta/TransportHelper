import flet as ft

from . import fin_trayecto, home, inicio, ayuda



def get_debug_view(page: ft.Page) -> ft.View:
    page.title = "MENÚ DEBUG 🙉"
    view = ft.View()

    def ir_a_fin_viaje(e):
        page.views.append(fin_trayecto.get_fin_trayecto_view(page))
        page.go("/fin_trayecto")

    def ir_a_home(e):
        page.views.append(home.get_home_view(page))
        page.go("/home")

    def ir_a_inicio(e):
        page.views.append(inicio.get_home_view(page))  # Fixed: was get_home_view
        page.go("/inicio")

    def ir_a_ayuda(e):
        page.views.append(ayuda.get_ayuda_view(page))
        page.go("/ayuda")


    boton_fin_viaje = ft.OutlinedButton("fin_viaje", on_click=ir_a_fin_viaje)
    boton_ayuda = ft.OutlinedButton("ayuda", on_click=ir_a_ayuda)
    boton_home = ft.OutlinedButton("home", on_click=ir_a_home)
    boton_inicio = ft.OutlinedButton("inicio", on_click=ir_a_inicio)


    view.controls.extend([
        boton_fin_viaje,
        boton_home,
        boton_inicio,
        boton_ayuda

    ])

    return view
