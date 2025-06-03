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
import geocoder

g = geocoder.ip('me')
curr_lat, curr_lng = g.latlng

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
                    "src/assets/metro-subir.png")
        elif index == self.length_of_leg-1:
            return ("Bájate en la siguiente parada. El nombre de la parada es "+self.steps[index]["name"],
                    "src/assets/metro-bajar.png")
        return ("Quédate en el metro. Parada actual: " + self.steps[index]["name"],
                "src/assets/metro-dentro.png")

class CarPickup(Leg):
    def __init__(self, id_, data):
        super().__init__(id_, data)
        self.steps = []
        self.steps.insert(0, {"info": "start"})
        self.steps.append({"info": "end"})
        self.__set_length_of_leg()
    def __set_length_of_leg(self):
        self.length_of_leg = len(self.steps)

    def add_step(self, index):
        self.current_distance = self.full_distance

    def remove_step(self, index):
        self.current_distance = 0

    def get_instruction(self, index):
        if index == 0:
            return ("Espera por el taxi y súbete al taxi en " + self.data["steps"][index]["streetName"],
                    "src/assets/taxi-subir.png")
        elif index == self.length_of_leg-1:
            return ("Bájate del taxi cuando llegues. El nombre del lugar es "+self.data["to"]["name"],
                    "src/assets/taxi-bajar.png")
        return ("Quédate en el taxi. Te encuentras actualmente en: " + self.data["steps"][index]["streetName"],
                "src/assets/taxi-dentro.png")

def get_trayecto_view(page: ft.Page) -> ft.View:
    page.title = "Tu Trayecto"
    from datetime import datetime

    # Get current datetime
    now = datetime.now()

    # Format time as h:mmam/pm (e.g., 10:40am)
    time_str = now.strftime("%I:%M%p").lower()  # "%I" is hour (01-12), "%M" is minutes, "%p" is AM/PM
    # Remove leading zero from hour (e.g., '09:30am' -> '9:30am')
    if time_str[0] == '0':
        time_str = time_str[1:]

    # Format date as mm-dd-yyyy (e.g., 05-16-2025)
    date_str = now.strftime("%m-%d-%Y")

    url = (
            "http://otp.danielcuesta.es/otp/routers/default/plan?fromPlace="
            + str(curr_lat) + "%2C" + str(curr_lng)
            + "&toPlace=" + str(page.client_storage.get("dest_lat")) + "%2C" + str(page.client_storage.get("dest_lng"))
            + "&time=" + time_str
            + "&date=" + date_str
            + "&mode=" + page.client_storage.get("transporte")
            + "&arriveBy=false&wheelchair=false&showIntermediateStops=true&locale=en"
    )
    def finish_trayecto(e):
        page.views.append(fin_trayecto.get_fin_trayecto_view(page))
        page.client_storage.set("transporte", "")
        page.go("/fin_trayecto")

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
            if isinstance(curr_leg, Walk):
                remaining_distance_text.current.value = "Distancia restante hasta siguiente punto: " + str(
                    curr_leg.steps[current_step_index]["distance"]) + " metros"
                paradas_restantes_text.current.value = ""
            elif isinstance(curr_leg, Bus) or isinstance(curr_leg, Subway):
                paradas_restantes_text.current.value = "Quedan "+str(len(curr_leg.steps)-current_step_index)+" paradas"
            else:
                remaining_distance_text.current.value = ""
                paradas_restantes_text.current.value = ""

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
            instruction_image_ref.current.src = "src/assets/goal.png"
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
            if not goal_almost_reached:
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
            else:
                goal_almost_reached = False
                remaining_time += (legs[current_leg_index]).duration
                update_instruction(-1)

    headers = {"Content-Type": "application/json"}
    route_data = requests.get(url, headers=headers).json()


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
    instr_flet_image = ft.GestureDetector(
        on_tap=next_step,
        content=ft.Image(
            src="",
            ref=instruction_image_ref,
            width=100,
            height=100,
            fit=ft.ImageFit.CONTAIN
        )
    )
    confirm_cancel_dialog = ft.Ref()

    def go_to_home():
        if page.views:
            page.views.pop()
            page.views.pop()
        page.go("/home")  # Or your actual home route

    def show_confirm_cancel_dialog(e):
        confirm_cancel_dialog.current.open = True
        page.update()

    dialog_cancel_trip = ft.AlertDialog(
        ref=confirm_cancel_dialog,
        modal=True,
        title=ft.Text("¿Cancelar trayecto?"),
        content=ft.Text("¿Estás seguro de que quieres cancelar el trayecto actual?"),
        actions=[
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_color=ft.colors.RED,
                on_click=lambda e: (setattr(confirm_cancel_dialog.current, "open", False), page.update())
            ),
            ft.IconButton(
                icon=ft.icons.CHECK,
                icon_color=ft.colors.GREEN,
                on_click=lambda e: go_to_home()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

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
            elif leg_data["mode"] == "CAR":
                leg = CarPickup(i, leg_data)
            else:
                leg = None
                raise Exception("Unknown leg mode")
            remaining_time += leg_data["duration"]
            legs.append(leg)
        print("Start Remaining time: ", remaining_time)


    except Exception as e:
        print("Error al cargar ruta:", e)




    update_instruction(1)

    return ft.View(
        route="/trayecto",
        controls=[
            ft.SafeArea(
                ft.Container(
                    bgcolor=ft.colors.WHITE,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.GestureDetector(
                                        on_tap=show_confirm_cancel_dialog,
                                        content=ft.CircleAvatar(
                                            content=ft.Image(
                                                src="src/assets/bus_not_black.png",
                                                width=30,
                                                height=30,
                                                fit=ft.ImageFit.CONTAIN,
                                            ),
                                            bgcolor=ft.colors.LIGHT_BLUE_200,
                                        ),
                                    ),
                                    ft.Text("T.H.", size=20, weight="bold", color=ft.colors.BLACK),
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK,
                                        icon_color=ft.colors.WHITE,
                                        bgcolor=ft.colors.DEEP_ORANGE,
                                        on_click=show_confirm_cancel_dialog,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),

                            ft.Container(
                                content=ft.Text("Itinerario", size=18, weight="bold", color=ft.colors.BLACK),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(bottom=5),
                            ),

                            ft.Column(
                                [
                                    arrival_flet,
                                    remaining_flet_time,
                                    paradas_flet_text,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),

                            ft.Container(
                                content=ft.Text("Sigue la siguiente instrucción:", size=18, weight="bold", color=ft.colors.BLACK),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(top=20, bottom=5),
                            ),

                            ft.Column(
                                [
                                    remaining_flet_distance,
                                    instr_flet_image,
                                    instr_flet_text,
                                    found_place_button,
                                    ft.Row(
                                        [
                                            ft.Column(
                                                [
                                                    ft.Text("Retrocede al paso anterior", size=12,
                                                            color=ft.colors.BLACK),
                                                    ft.IconButton(
                                                        icon=ft.icons.ARROW_LEFT,
                                                        icon_color=ft.colors.WHITE,
                                                        bgcolor=ft.colors.BLUE,
                                                        icon_size=40,
                                                        width=60,
                                                        height=60,
                                                        on_click=previous_step,
                                                        tooltip="Paso anterior",
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text("Avanza al siguiente paso", size=12, color=ft.colors.BLACK),
                                                    ft.IconButton(
                                                        icon=ft.icons.ARROW_RIGHT,
                                                        icon_color=ft.colors.WHITE,
                                                        bgcolor=ft.colors.BLUE,
                                                        icon_size=40,
                                                        width=60,
                                                        height=60,
                                                        on_click=next_step,
                                                        tooltip="Siguiente paso",
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=40,
                                    ),

                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),

                            dialog_cancel_trip,
                        ],
                        spacing=15,
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    width=None,
                )
            ),
        ],
    )
