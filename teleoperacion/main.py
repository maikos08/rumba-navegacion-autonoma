"""Teleoperación con odometría: conduces desde la web y ves la posición. Ver README.md."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto

from rumba.ejecutar import Tarea, lanzar   # noqa: E402
from rumba.geometria import normalizar     # noqa: E402
from rumba.robot import Rastro             # noqa: E402


class Teleoperacion(Tarea):
    pagina = Path(__file__).resolve().parent / "ui.html"

    def __init__(self, cfg):
        super().__init__()
        self.rastro = Rastro(cfg.min_paso)
        self.vr = self.vl = 0
        self.salir = False
        # tecla -> (velocidad rueda derecha, velocidad rueda izquierda)
        self.comandos = {
            "w": (cfg.v_avance, cfg.v_avance),    # avanzar
            "a": (cfg.v_giro, -cfg.v_giro),       # girar a la izquierda
            "d": (-cfg.v_giro, cfg.v_giro),       # girar a la derecha
            "p": (0, 0),                          # parar
        }

    def paso(self, m):
        if self.salir:
            return None
        self.rastro.actualizar(m.x, m.y, m.theta)
        return self.vr, self.vl

    def linea_consola(self, m):
        grados = math.degrees(normalizar(m.theta))
        return f"\rx = {m.x:8.1f} mm   y = {m.y:8.1f} mm   θ = {grados:7.1f}°   "

    def estado_web(self, args):
        return self.rastro.para_web(args)

    def acciones_web(self):
        return {"/cmd": self.comando}

    def comando(self, args):
        c = args.get("c", "")
        if c in self.comandos:
            self.vr, self.vl = self.comandos[c]
        elif c == "q":
            self.salir = True


def main(robot=None):
    lanzar(Teleoperacion, robot=robot)


if __name__ == "__main__":
    main()
