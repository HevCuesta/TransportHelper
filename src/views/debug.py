import flet as ft

from views import fin_viaje, home, inicio, recuperar_contrasena, register, ayuda



def get_debug_view(page: ft.Page) -> ft.View:
    page.title = "MENÚ DEBUG 🙉"
    view = ft.View()

    def ir_a_fin_viaje(e):
        page.views.append(fin_viaje.get_fin_viaje_view(page))
        page.go("/fin_viaje")

    def ir_a_home(e):
        page.views.append(home.get_home_view(page))
        page.go("/home")

    def ir_a_inicio(e):
        page.views.append(inicio.get_home_view(page))  # Fixed: was get_home_view
        page.go("/inicio")

    def ir_a_recuperar_contrasena(e):
        page.views.append(recuperar_contrasena.get_recuperar_contrasena_view(page))
        page.go("/recuperar_contrasena")

    def ir_a_register(e):
        page.views.append(register.get_register_view(page))
        page.go("/register")
    def ir_a_ayuda(e):
        page.views.append(ayuda.get_ayuda_view(page))
        page.go("/ayuda")


    boton_fin_viaje = ft.OutlinedButton("fin_viaje", on_click=ir_a_fin_viaje)
    boton_ayuda = ft.OutlinedButton("ayuda", on_click=ir_a_ayuda)
    boton_home = ft.OutlinedButton("home", on_click=ir_a_home)
    boton_inicio = ft.OutlinedButton("inicio", on_click=ir_a_inicio)
    boton_recuperar_contrasena = ft.OutlinedButton("recuperar_contraseña", on_click=ir_a_recuperar_contrasena)

    view.controls.extend([
        boton_fin_viaje,
        boton_home,
        boton_inicio,
        boton_login,
        boton_recuperar_contrasena,
        boton_register,
        boton_ayuda

    ])

    return view
