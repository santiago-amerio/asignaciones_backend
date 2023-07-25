import http3
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class horarios:
    def __init__(self, legajo: str):
        self.legajo = legajo
        self.url = f"{os.getenv('ALSEA_URL')}{self.legajo}"
        self.horarios = ""
        self.current_date = datetime.now()

    async def load_horarios(self):
        client = http3.AsyncClient()
        r = await client.get(self.url)
        json = self.__fix_date_horarios(r.json())
        self.horarios = json
        return json

    def get_first_day(self, index=0):
        return self.horarios["asignaciones"][index]

    def get_one_day(self, day: str):
        fecha = day.replace("-", "/")
        for index, asignacion in enumerate(self.horarios["asignaciones"]):
            if asignacion["fecha"] == fecha:
                return asignacion
        return

    def get_all_days(self):
        return self.horarios

    def __fix_date_horarios(self, json):
        # 21/07/2023 14:00
        json["fechaConsulta"] = datetime.strptime(
            json["fechaConsulta"], "%d/%m/%Y %H:%M"
        )
        for index, horario in enumerate(json["asignaciones"]):
            api_day_week, formatted_date = self.__format_fecha(horario)
            hora_entrada, hora_salida = self.__format_horaE_horaS(
                horario, formatted_date
            )
            json["asignaciones"][index]["horaEntrada"] = hora_entrada
            json["asignaciones"][index]["horaSalida"] = hora_salida
            json["asignaciones"][index]["fecha"] = formatted_date
            json["asignaciones"][index]["diaSemana"] = api_day_week
            json["asignaciones"][index]["fechaConsulta"] = json["fechaConsulta"]
            json["asignaciones"][index]["legajo"] = json["legajo"]
        return json

    def __format_fecha(self, horario):
        current_year = self.current_date.year
        current_month = self.current_date.month
        api_date = horario["fecha"].replace(" ", "/")
        api_day_week, api_day, api_month = api_date.split("/")
        api_day = int(api_day)
        api_month = int(api_month)
        api_year = current_year + 1 if api_month < current_month else current_year
        formatted_date = f"{api_day}/{api_month}/{api_year}"
        formatted_date = datetime.strptime(formatted_date, "%d/%m/%Y")
        return (api_day_week, formatted_date)

    def __format_horaE_horaS(self, horario, formatted_date):
        horaE = horario["horaEntrada"]
        horaS = horario["horaSalida"]
        horaE = formatted_date.replace(hour=int(horaE.split(":")[0])).replace(
            minute=int(horaE.split(":")[1])
        )
        horaS = formatted_date.replace(hour=int(horaS.split(":")[0])).replace(
            minute=int(horaS.split(":")[1])
        )
        if horaS < horaE:
            horaS = horaS + timedelta(days=1)
        return horaE, horaS


class Horario_alsea(BaseModel):
    tienda: str
    legajo: str
    fecha: date
    diaSemana: str
    horaEntrada: datetime
    horaSalida: datetime
    fechaConsulta: datetime


class Horarios_alsea(BaseModel):
    asignaciones: list[Horario_alsea]
