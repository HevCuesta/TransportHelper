# Código completo con la lógica ajustada
import flet as ft
from curl_cffi import requests
from views import elegir_transporte
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

class Leg:
    def __init__(self, id_, data):
        self.id = id_
        self.mode = data.get("mode")
        self.start_time = data.get("startTime")
        self.arrival = data.get("endTime")
        self.end_time = data.get("endTime")
        self.full_distance = data.get("distance")
        self.current_distance = 0
        self.duration = data.get("duration")
        print("Created leg with duration "+str(self.duration))
        self.data = data
        self.length_of_leg = 0
class Walk(Leg):
    def __init__(self, id_, data):
        super().__init__(id_, data)
        self.steps = data.get("steps", [])
        # Distancia actualmente recorrida
        self.__set_length_of_leg()
    def __set_length_of_leg(self):
        self.length_of_leg = len(self.data.get("steps", []))

class Bus(Leg):
    def __init__(self, id_, data):
        super().__init__(id_, data)
        self.route = data.get("route")
        self.stops = data.get("intermediateStops", [])
        self.stops.insert(0,data.get("from"))
        self.stops.append(data.get("to"))
        self.current_stop = 0
        self.__set_length_of_leg()
    def __set_length_of_leg(self):
        self.length_of_leg = len(self.data.get("intermediateStops", []))+2


def get_trayecto_view(page: ft.Page) -> ft.View:
    page.title = "Tu Trayecto"
    url = "http://localhost:8080/otp/routers/default/plan?fromPlace=40.41907%2C-3.69626&toPlace=40.42516075030649%2C-3.683724445593922&time=10%3A22am&date=05-16-2025&mode=" + page.client_storage.get("transporte") + "&arriveBy=false&wheelchair=false&showIntermediateStops=true&locale=en"

    headers = {"Content-Type": "application/json"}
    route_data = requests.get(url, headers=headers).json()

    instruction_text = ft.Ref()
    instr_flet_text = ft.Text("", ref=instruction_text, color=ft.colors.BLACK)

    remaining_time_text = ft.Ref()
    remaining_flet_time = ft.Text("", ref=remaining_time_text, color=ft.colors.BLACK)

    remaining_distance_text = ft.Ref()
    remaining_flet_distance = ft.Text("", ref=remaining_distance_text, color=ft.colors.BLACK)

    paradas_restantes_text = ft.Ref()
    paradas_flet_text = ft.Text("", ref=paradas_restantes_text, color=ft.colors.BLACK)

    arrival_text = ft.Ref()
    arrival_flet = ft.Text("", ref=arrival_text, color=ft.colors.BLACK)

    instruction_image_ref = ft.Ref()
    instr_flet_image = ft.Image(src="", ref=instruction_image_ref, width=100, height=100, fit=ft.ImageFit.CONTAIN)

    current_leg_index = 0
    current_step_index = 0
    legs = []
    remaining_time = 0  # en segundos
    tiempo_diferencia_acumulado = 0.0



    try:
        itineraries = route_data["plan"]["itineraries"]
        fastest_itinerary = min(itineraries, key=lambda x: x["duration"])
        remaining_time = fastest_itinerary["duration"]
        for i, leg_data in enumerate(fastest_itinerary["legs"]):
            if leg_data["mode"] == "WALK":
                leg = Walk(i, leg_data)
            elif leg_data["mode"] == "BUS":
                leg = Bus(i, leg_data)
            else:
                leg = Leg(i, leg_data)
            legs.append(leg)


    except Exception as e:
        print("Error al cargar ruta:", e)

    def go_to_elegir_transporte():
        if page.views:
            page.views.pop()
        page.views.append(elegir_transporte.get_elegir_transporte_view(page))
        page.go("/elegir_transporte")

    def update_instruction(pn_step): #1 si pasamos a la siguiente instrucción, -1 si volvemos atrás
        nonlocal remaining_time
        print("Remaining " + str(remaining_time))
        if pn_step == 1 or pn_step == -1:
            curr_leg = legs[current_leg_index]
            if isinstance(curr_leg, Walk):
                curr_leg.current_distance += curr_leg.steps[current_step_index]["distance"]*pn_step
                distancia_leg = curr_leg.full_distance
                progreso_dist = (curr_leg.current_distance / distancia_leg)
                progreso_tiempo = (
                        (1747383763*1000 - curr_leg.start_time) / (curr_leg.end_time - curr_leg.start_time))
                multiplicador = progreso_dist / progreso_tiempo
                print(curr_leg.duration)
                curr_leg.arrival = curr_leg.end_time / multiplicador*pn_step

                remaining_leg_time = remaining_time - (curr_leg.duration-curr_leg.duration*(1-progreso_dist))
                remaining_time_text.current.value = f"Tiempo restante: {int(remaining_leg_time)//60} min"
                arrival_text.current.value = f"Hora de llegada: {datetime.fromtimestamp(1747383763+remaining_leg_time).strftime("%H:%M")}"
                instruction_text.current.value = (
                        curr_leg.steps[current_step_index]["relativeDirection"] + " por " +
                        curr_leg.steps[current_step_index]["streetName"])
                remaining_distance_text.current.value = "Remaining distance: " + str(
                    curr_leg.steps[current_step_index]["distance"])
                instruction_image_ref.current.src = "src/assets/go-straight.png"
            if isinstance(curr_leg, Bus):
                pass
                # Remaining time
                # Start time general y end time general de bus
                # Arrival y departure son franjas en los que pasa el autobús (isNonExactFrecuency = true)
            page.update()



    def next_step(e):
        nonlocal current_step_index, current_leg_index, tiempo_diferencia_acumulado, remaining_time
        if legs:
            if current_step_index < legs[current_leg_index].length_of_leg - 1:
                current_step_index += 1
                update_instruction(1)
            else:
                if current_leg_index < len(legs) - 1:
                    # Si terminó el leg, restar tiempo del del al tiempo restante (hasta este punto sólo se restaba visualmente)
                    remaining_time -= (legs[current_leg_index]).duration
                    current_step_index = 0
                    current_leg_index += 1
                    update_instruction(1)
                else:
                    #Se ha llegado al destino
                    pass


    def previous_step(e):
        nonlocal current_step_index, current_leg_index, tiempo_diferencia_acumulado, remaining_time
        if legs:
            if current_step_index > 0:
                current_step_index -= 1
                update_instruction(-1)
            else:
                if current_leg_index > 0:
                    remaining_time += (legs[current_leg_index]).duration
                    current_leg_index -= 1
                    current_step_index = legs[current_leg_index].length_of_leg - 1
                    update_instruction(-1)
                else:
                    #Se ha llegado al inicio del trayecto
                    pass



    update_instruction(1)

    return ft.View(
        route="/trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.CircleAvatar(
                                content=ft.Image(
                                    src="src/assets/bus_not_black.png",
                                    width=30,
                                    height=30,
                                    fit=ft.ImageFit.CONTAIN,
                                ),
                                bgcolor=ft.colors.LIGHT_BLUE_200,
                            ),
                            ft.Text("T.H.", size=20, weight="bold"),
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                icon_color=ft.colors.WHITE,
                                bgcolor=ft.colors.DEEP_ORANGE,
                                on_click=go_to_elegir_transporte,
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Text("Tu Trayecto", size=24, weight="bold", text_align="center"),

                        ft.Container(
                            content=ft.Column([
                                ft.Text("Resumen del trayecto", size=18, weight="bold"),
                                ft.Text("Medio: " + page.client_storage.get("transporte")),
                                arrival_flet,
                                remaining_flet_time,
                                paradas_flet_text,
                                ft.Container(
                                    height=200,
                                    bgcolor=ft.colors.GREY_200,
                                    border_radius=10,
                                    alignment=ft.alignment.center,
                                    content=ft.Text("Mapa del trayecto (opcional)"),
                                )
                            ], spacing=5),
                            padding=20,
                            bgcolor=ft.colors.LIGHT_BLUE_50,
                            border_radius=10
                        ),

                        ft.Container(
                            content=ft.Column([
                                ft.Text("Instrucción actual:", size=18, weight="bold"),
                                remaining_flet_distance,
                                instr_flet_image,
                                instr_flet_text,
                                ft.Row([
                                    ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=previous_step),
                                    ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=next_step),
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ], spacing=5),
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=10
                        )
                    ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.top_center,
                    expand=True
                )
            )
        ]
    )