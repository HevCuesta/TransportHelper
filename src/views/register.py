import flet as ft

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
    
    # Note: This function needs to return a ft.View object
    # Here's a basic implementation:
    return ft.View(
        route="/register",
        controls=[
            ft.Column(controls=[
                username,
                email
            ])
        ]
    )