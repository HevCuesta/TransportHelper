import flet as ft
from views import login

def get_register_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Register"

    username = ft.TextField(  # Fixed typo: TextFileld -> TextField
        label = "Usuario",    # Fixed typo: username -> label
        border = ft.InputBorder.OUTLINE,
        prefix_icon = ft.Icons.PERSON
    )

    email = ft.TextField(     # Fixed typo: TextFileld -> TextField
        label = "correo",
        border = ft.InputBorder.OUTLINE,
        prefix_icon = ft.Icons.EMAIL
    )

    def register_click(e):
        pass

    def go_to_login(e):
        page.views.append(login.get_login_view(page))
        # Navigate directly to login page on startup
        page.go("/login")



    # Note: This function needs to return a ft.View object
    # Here's a basic implementation:
    return ft.View(
        route="/register",
        controls=[
            ft.SafeArea(
                ft.Container(
                    ft.Column(
                        [
                            ft.Image(
                                src="src/assets/bus_black.png" if page.theme_mode == ft.ThemeMode.DARK else "src/assets/bus_not_black.png",
                                width=150,
                                height=150,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text("TransportHelper", size=30, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=20, color="transparent"),
                            username,
                            email,
                            ft.ElevatedButton(
                                text="Registrarse",
                                width=320,
                                on_click=register_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            ),
                            ft.FilledButton(
                                "¿Ya tienes cuenta?",
                                bgcolor="lightblue",
                                on_click=go_to_login
                            ),
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


