import flet as ft
from views import login

def get_recuperar_contrasena_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper - Recuperar Contraseña"
    status_text = ft.Text("", color="red")
    # Recovery fields
    email = ft.TextField(
        label="Correo electrónico",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.Icons.EMAIL
    )

    def volver_login(_):
        page.views.append(login.get_login_view(page))
        # Navigate directly to login page on startup
        page.go("/login")
        
    # Success dialog popup
    success_dialog = ft.AlertDialog(
        title=ft.Text("Recuperación de Contraseña"),
        content=ft.Text("Correo de recuperación enviado"),
        actions=[
            ft.TextButton("Volver a inicio de sesión", on_click=volver_login)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def show_success_dialog(_):
        page.dialog = success_dialog
        success_dialog.open = True
        
    def recovery_click(e):
        if not email.value:
            status_text.value = "Por favor, introduce tu correo electrónico"
            status_text.update()
        else:
            # Aquí puedes agregar lógica para enviar correo de recuperación
            show_success_dialog(e)
        page.go("/login")

    # Botón de volver a la izquierda
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color="pink",
        tooltip="Volver",
        on_click=volver_login,
    )

    return ft.View(
        route="/recuperar-contrasena",
        controls=[
            ft.SafeArea(
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [back_button, ft.Container(expand=True)],
                                alignment=ft.MainAxisAlignment.START
                            ),
                            ft.Image(
                                src="src/assets/bus_black.png" if page.theme_mode == ft.ThemeMode.DARK else "src/assets/bus_not_black.png",
                                width=150,
                                height=150,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text("TransportHelper", size=30, weight=ft.FontWeight.BOLD),
                            ft.Text("Recuperar Contraseña", size=20),
                            ft.Divider(height=20, color="transparent"),
                            email,
                            status_text,
                            ft.ElevatedButton(
                                text="Enviar enlace de recuperación",
                                width=320,
                                on_click=recovery_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            )
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
