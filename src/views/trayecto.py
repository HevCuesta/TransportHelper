# Código completo con la lógica ajustada
import flet as ft
from curl_cffi import requests
from views import elegir_transporte, fin_trayecto
import time
from datetime import datetime
import warnings
import re
warnings.filterwarnings("ignore")
import json

with  open("src/instruction_converter.json", "r", encoding="utf-8") as file:
    instruction_converter = json.load(file)

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

    def add_step(self, index):
        self.current_distance += self.steps[index]["distance"]

    def remove_step(self, index):
        self.current_distance -= self.steps[index]["distance"]

    def get_instruction(self, index):
        #returns a tuple of the text formed + the image to be used
        if "sidewalk" in self.steps[index]["streetName"]:
            # Si no hay nombre de calle
            info_return = instruction_converter[self.steps[index]["absoluteDirection"]]
            return (info_return["text"],
                    info_return["img"])
        info_return = instruction_converter[self.steps[index]["relativeDirection"]]
        if "CLOCK" in self.steps[index]["relativeDirection"]:
            # Rotonda
            return (info_return["text"] +
                    self.steps[index]["exit"],
                    info_return["img"])
        else:
            # Otra instrucción
            return (info_return["text"] +
                    " por " +
                    self.steps[index]["streetName"],
                    info_return["img"])

class Bus(Leg):
    def __init__(self, id_, data):
        super().__init__(id_, data)
        self.route = data.get("route")
        self.steps = data.get("intermediateStops", [])
        self.steps.insert(0, data.get("from"))
        self.steps.append(data.get("to"))
        self.__set_length_of_leg()
    def __set_length_of_leg(self):
        self.length_of_leg = len(self.steps)

    def add_step(self, index):
        time_arrival_to_step = self.steps[index]["departure"]
        time_progress = (time_arrival_to_step - self.start_time)/(self.end_time - self.start_time)
        self.current_distance = self.full_distance*time_progress

    def remove_step(self, index):
        time_arrival_to_step = self.steps[index]["departure"]
        time_progress = (time_arrival_to_step - self.start_time) / (self.end_time - self.start_time)
        self.current_distance = self.full_distance * time_progress

    def get_instruction(self, index):
        if index == 0:
            return ("Súbete al autobús "+self.steps[index]["stopId"].split(':')[0] + " en " + self.steps[index]["name"],
                    "src/assets/bus-subir.png")
        elif index == self.length_of_leg-1:
            return ("Bájate en la siguiente parada. El nombre de la parada es "+self.steps[index]["name"],
                    "src/assets/bus-bajar.png")
        return ("Quédate en el bus. Parada actual: " + self.steps[index]["name"],
                "src/assets/bus-avanzar.png")

class Subway(Leg):
    def __init__(self, id_, data):
        super().__init__(id_, data)
        self.route = data.get("route")
        self.subway_Id = data.get("routeId")
        self.steps = data.get("intermediateStops", [])
        self.steps.insert(0, data.get("from"))
        self.steps.append(data.get("to"))
        self.__set_length_of_leg()
    def __set_length_of_leg(self):
        self.length_of_leg = len(self.steps)
    def add_step(self, index):
        time_arrival_to_step = self.steps[index]["departure"]
        time_progress = (time_arrival_to_step - self.start_time)/(self.end_time - self.start_time)
        self.current_distance = self.full_distance*time_progress
    def remove_step(self, index):
        time_arrival_to_step = self.steps[index]["departure"]
        time_progress = (time_arrival_to_step - self.start_time) / (self.end_time - self.start_time)
        self.current_distance = self.full_distance * time_progress
    def get_instruction(self, index):
        if index == 0:
            match = re.match(r"(\d+):(\d+)__([\d]+)___", self.subway_Id)
            return ("Súbete al metro " + match.group(3) + " en " + self.steps[index]["name"],
                    "src/assets/go-straight.png")
        elif index == self.length_of_leg-1:
            return ("Bájate en la siguiente parada. El nombre de la parada es "+self.steps[index]["name"],
                    "src/assets/down-arrow.png")
        return ("Quédate en el metro. Parada actual: " + self.steps[index]["name"],
                "src/assets/go-straight.png")

def get_trayecto_view(page: ft.Page) -> ft.View:
    page.title = "Tu Trayecto"
    url = "https://otp.danielcuesta.es/otp/routers/default/plan?fromPlace=40.450735382579694%2C-3.6938953399658208&toPlace=40.4281%2C-3.70213&time=10%3A40am&date=05-16-2025&mode="+page.client_storage.get("transporte")+"&arriveBy=false&wheelchair=false&showIntermediateStops=true&locale=en"
    def finish_trayecto(e):
        page.views.append(fin_trayecto.get_fin_trayeto_view(page))
        page.client_storage.set("transporte", "")
        page.go("/fin_trayecto")

    headers = {"Content-Type": "application/json"}
    route_data = requests.get(url, headers=headers).json()

    with open("src/delete.json", "w", encoding="utf-8") as f:
        json.dump(route_data, f, ensure_ascii=False, indent=2)

    instruction_text = ft.Ref()
    instr_flet_text = ft.Text("", ref=instruction_text, color=ft.colors.BLACK)

    found_place_button = ft.ElevatedButton(
        text="Pulsa aquí si encontraste el lugar",
        icon=ft.icons.ARROW_FORWARD,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.colors.DEEP_ORANGE,
            color=ft.colors.WHITE
        ),
        visible=False,
        width=300,
        on_click=finish_trayecto
    )


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
    goal_almost_reached = False

    try:
        itineraries = route_data["plan"]["itineraries"]
        fastest_itinerary = min(itineraries, key=lambda x: x["duration"])
        for i, leg_data in enumerate(fastest_itinerary["legs"]):
            if leg_data["mode"] == "WALK":
                leg = Walk(i, leg_data)
            elif leg_data["mode"] == "BUS":
                leg = Bus(i, leg_data)
            elif leg_data["mode"] == "SUBWAY":
                leg = Subway(i, leg_data)
            else:
                leg = Leg(i, leg_data)
            remaining_time += leg_data["duration"]
            legs.append(leg)
        print("Start Remaining time: ", remaining_time)


    except Exception as e:
        print("Error al cargar ruta:", e)

    def go_to_elegir_transporte():
        if page.views:
            page.views.pop()
        page.views.append(elegir_transporte.get_elegir_transporte_view(page))
        page.go("/elegir_transporte")

    def update_instruction(pn_step): #1 si pasamos a la siguiente instrucción, -1 si volvemos atrás, 0 si hemos llegado a destino
        nonlocal remaining_time
        if pn_step == 1 or pn_step == -1:
            curr_leg = legs[current_leg_index]
            progreso_dist = (curr_leg.current_distance / curr_leg.full_distance)
            print(progreso_dist)
            print("Rt: "+str(remaining_time))
            progreso_tiempo = (
                    (time.time()*1000 - curr_leg.start_time) / (curr_leg.end_time - curr_leg.start_time))
            multiplicador = progreso_dist / progreso_tiempo
            if multiplicador == 0:
                curr_leg.arrival = curr_leg.end_time+(time.time()*1000 - curr_leg.start_time)
            else:
                curr_leg.arrival = curr_leg.end_time / multiplicador*pn_step
            remaining_leg_time = remaining_time - (curr_leg.duration-curr_leg.duration*(1-progreso_dist))
            remaining_time_text.current.value = f"Tiempo restante: {int(remaining_leg_time)//60} min"
            arrival_text.current.value = f"Hora de llegada: {datetime.fromtimestamp(time.time()+remaining_leg_time).strftime("%H:%M")}"
            if not isinstance(curr_leg, Bus) and not isinstance(curr_leg, Subway):
                remaining_distance_text.current.value = "Distancia restante hasta siguiente punto: " + str(
                    curr_leg.steps[current_step_index]["distance"])
            else:
                remaining_distance_text.current.value = ""

            display_info = curr_leg.get_instruction(current_step_index)
            instruction_text.current.value = display_info[0]
            instruction_image_ref.current.src = display_info[1]
            found_place_button.visible = False
            page.update()
        if pn_step == 0:
            found_place_button.visible = True
            remaining_distance_text.current.value = ""
            remaining_time_text.current.value = f"Tiempo restante: 0 min"
            arrival_text.current.value = f"Hora de llegada: {datetime.fromtimestamp(time.time()).strftime("%H:%M")}"
            instruction_text.current.value = f"Mira a ver si encuentras tu destino"
            instruction_image_ref.current.src = "/src/assets/goal-flag.png"
            # Hacer que te lleve al final
            page.update()



    def next_step(e):
        nonlocal current_step_index, current_leg_index, remaining_time, goal_almost_reached
        if legs:
            if current_step_index < legs[current_leg_index].length_of_leg - 1:
                legs[current_leg_index].add_step(current_step_index)
                current_step_index += 1
                update_instruction(1)
            else:
                if current_leg_index < len(legs) - 1:
                    # Si terminó el leg, restar tiempo del del al tiempo restante (hasta este punto sólo se restaba visualmente)
                    remaining_time -= legs[current_leg_index].duration
                    legs[current_leg_index].add_step(current_step_index)
                    current_step_index = 0
                    current_leg_index += 1
                    update_instruction(1)
                else:
                    if not goal_almost_reached:
                        remaining_time -= (legs[current_leg_index]).duration
                        goal_almost_reached = True
                        update_instruction(0)
                    else:
                        print("Se ha llegado al destino")
                    pass


    def previous_step(e):
        nonlocal current_step_index, current_leg_index, remaining_time, goal_almost_reached
        if legs:
            goal_almost_reached = False
            if current_step_index > 0:
                current_step_index -= 1
                legs[current_leg_index].remove_step(current_step_index)
                update_instruction(-1)
            else:
                if current_leg_index > 0:
                    current_leg_index -= 1
                    current_step_index = legs[current_leg_index].length_of_leg - 1
                    legs[current_leg_index].remove_step(current_step_index)
                    remaining_time += (legs[current_leg_index]).duration
                    update_instruction(-1)
                else:
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
                                found_place_button,
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