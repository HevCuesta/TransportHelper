import os.path

import flet as ft
import json
def get_instrucciones_view(page:ft.Page) -> ft.View:
    page.title = "Resolución de problemas"
    json.JSONDecoder()
    dir = os.path.join("src","assets","instrucciones.json")
    with open(dir) as f:
        json.load(f)

    return ft.view(route="/instrucciones")
