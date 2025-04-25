import flet as ft

def get_login_view(page: ft.Page) -> ft.View:
    page.title = "TransportHelper Login"

    # Login fields
    username = ft.TextField(
        label="Username",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.PERSON
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.LOCK
    )

    # Status
    status_text = ft.Text("", color="red")

    def login_click(e):
        if not username.value or not password.value:
            status_text.value = "Please fill in all fields"
            status_text.color = "red"
        else:
            status_text.value = f"Trying to login as {username.value}..."
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
                            ft.Text("TransportHelper", size=30, weight=ft.FontWeight.BOLD),
                            ft.Text("Login to your account", size=16),
                            ft.Divider(height=20, color="transparent"),
                            username,
                            password,
                            status_text,
                            ft.ElevatedButton(
                                text="Login",
                                width=320,
                                on_click=login_click,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                )
                            ),
                            ft.TextButton("Forgot password?"),
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
