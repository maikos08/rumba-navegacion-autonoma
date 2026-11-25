"""
Tarea de exploración: el robot ejecuta un modo SIN objetivo (limpieza o seguir_pared)
desde que se pulsa Iniciar en la web hasta que se pulsa Parar.
La usan limpieza/ y seguir_pared/ (misma página: exploracion.html).
"""
import math
from pathlib import Path

from rumba.ejecutar import Tarea
from rumba.geometria import normalizar
from rumba.navegacion import Navegador
from rumba.robot import Rastro


class TareaExploracion(Tarea):
    pagina = Path(__file__).resolve().parent / "exploracion.html"

    def __init__(self, cfg, modo, titulo):
        super().__init__()
        self.rastro = Rastro(cfg.min_paso)
        self.nav = Navegador(cfg, modo)
        self.titulo = titulo
        self.activo = False
        self.arrancar = False     # la web acaba de pulsar Iniciar
        self.salir = False
        self.estado = "Pulsa Iniciar"
        self.ir = [0] * 6

    def paso(self, m):
        self.ir = list(m.ir)
        if self.salir:
            return None
        if self.arrancar:
            self.arrancar = False
            self.nav.nuevo_trayecto(m.ahora)

        vr = vl = 0
        if self.activo:
            vr, vl, self.estado, _ = self.nav.paso(m, None, None)
        self.rastro.actualizar(m.x, m.y, m.theta)
        return vr, vl

    def linea_consola(self, m):
        grados = math.degrees(normalizar(m.theta))
        return (f"\rx = {m.x / 1000:7.3f} m   y = {m.y / 1000:7.3f} m   θ = {grados:7.1f}°   "
                f"{self.estado:<45}")

    def estado_web(self, args):
        datos = self.rastro.para_web(args)
        datos.update(estado=self.estado, modo=self.titulo, activo=self.activo, choques=self.nav.choques,
                     ir=self.ir, obstaculos=self.nav.obstaculos)
        return datos

    def acciones_web(self):
        return {"/cmd": self.comando}

    def comando(self, args):
        c = args.get("c", "")
        if c == "iniciar":
            self.activo = self.arrancar = True
        elif c == "parar":
            self.activo = False
            self.estado = "Parado"
        elif c == "q":
            self.salir = True
