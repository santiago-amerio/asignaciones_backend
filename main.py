from fastapi import FastAPI, HTTPException
from typing import Optional
import alsea

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/alsea/list/{legajo}/")
async def show_alsea_horarios(legajo: str) -> alsea.Horarios_alsea:
    horarios_instance = alsea.horarios(legajo)
    await horarios_instance.load_horarios()
    response = horarios_instance.get_all_days()
    return response


@app.get("/alsea/individual/{legajo}/")
async def show_alsea_horario(
    legajo: str, fecha: Optional[str] = None, index: Optional[int] = None
) -> alsea.Horario_alsea:
    horarios_instance = alsea.horarios(legajo)
    await horarios_instance.load_horarios()
    if fecha:
        horario_json = horarios_instance.get_one_day(fecha)
    else:
        horario_json = horarios_instance.get_first_day()
    if not horario_json:
        raise HTTPException(status_code=404, detail="fecha-not-found")

    return horario_json
