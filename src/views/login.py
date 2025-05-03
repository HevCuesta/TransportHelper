import flet as ft

def get_login_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Login"

    # Login fields
    username = ft.TextField(
        label="Nombre",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.Icons.PERSON
    )

    password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.Icons.LOCK
    )

    # Status
    status_text = ft.Text("", color="red")

    def login_click(e):
        if not username.value or not password.value:
            status_text.value = "Por favor, rellena los campos"
            status_text.color = "red"
        else:
            status_text.value = f"Iniciando sesión como {username.value}..."
            status_text.color = "green"
            # Aquí puedes agregar lógica de autenticación
        status_text.update()

    return ft.View(
        "/login",
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
                            password,
                            status_text,
                            ft.ElevatedButton(
                                text="Iniciar sesión",
                                width=320,
                                on_click=login_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            ),
                            ft.FilledButton("No recuerdo mi nombre o contraseña", bgcolor="lightblue"),
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
