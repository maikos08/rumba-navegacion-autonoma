"""
Ir a un punto (x, y). Contiene:

  - Navegador       : un trayecto hacia un objetivo con el modo elegido (carpeta modos/);
                      anota los choques y las marcas que se dibujan en el mapa
  - TareaObjetivo   : tarea "ir a UN objetivo" (la usan navegacion/ y evitar_obstaculos/)
  - elegir_modo()   : pregunta por consola parar / rodear
"""
import math

from rumba.ejecutar import Tarea
from rumba.geometria import normalizar
from rumba.modos import MODOS
from rumba.robot import Rastro


class Navegador:
    """Un ciclo de un trayecto: paso(m, objetivo, inicio) -> (vr, vl, estado, fin)."""

    def __init__(self, cfg, nombre_modo):
        self.cfg = cfg
        self.modo = MODOS[nombre_modo](cfg)    # "directo", "parar" o "bug2"
        self.obstaculos = []   # puntos de choque estimados (mm)
        self.encuentros = []   # puntos H donde Bug2 empieza a seguir un contorno
        self.salidas = []      # puntos donde Bug2 deja el contorno
        self.choques = 0

    def nuevo_trayecto(self, ahora):
        """Reinicia el modo (también sirve para cancelar el trayecto en curso)."""
        self.modo.iniciar(ahora)

    def limpiar_marcas(self):
        self.encuentros.clear()
        self.salidas.clear()

    def borrar_mapa(self):
        self.obstaculos.clear()
        self.limpiar_marcas()

    def paso(self, m, objetivo, inicio):
        if m.choque:
            c = self.cfg
            ang = math.radians(45) if (m.bump_izq and not m.bump_der) else \
                  math.radians(-45) if (m.bump_der and not m.bump_izq) else 0.0
            self.obstaculos.append((m.x + c.r_robot * math.cos(m.theta + ang),
                                    m.y + c.r_robot * math.sin(m.theta + ang)))
            self.choques += 1
        return self.modo.paso(self, m, objetivo, inicio)


def elegir_modo():
    """Pregunta por consola el modo. Devuelve ("parar" | "bug2", texto para la web)."""
    print("Modos de navegación:")
    print("  1 - Parar ante un obstáculo y continuar cuando se aparte")
    print("  2 - Rodear el obstáculo (Bug2)")
    eleccion = ""
    while eleccion not in ("1", "2"):
        eleccion = input("Elige modo (1/2): ").strip()
    texto = "1 (parar)" if eleccion == "1" else "2 (rodear)"
    print(f"Modo {texto}")
    return ("parar" if eleccion == "1" else "bug2"), texto


class TareaObjetivo(Tarea):
    """Ir a UN objetivo que se da desde la web (x, y en metros)."""

    def __init__(self, cfg, modo, pagina, texto_modo="", ancho_estado=32):
        super().__init__()
        self.pagina = pagina
        self.ancho_estado = ancho_estado
        self.rastro = Rastro(cfg.min_paso)
        self.nav = Navegador(cfg, modo)
        self.objetivo = None
        self.inicio = None
        self.nuevo = False       # la web acaba de dar un objetivo nuevo
        self.salir = False
        self.estado = "Sin objetivo"
        self.texto_modo = texto_modo
        self.ir = [0] * 6        # lectura de los light bumpers, para mostrarla

    def paso(self, m):
        self.ir = list(m.ir)
        if self.salir:
            return None
        if self.nuevo:
            self.nuevo = False
            self.inicio = (m.x, m.y)
            self.nav.limpiar_marcas()
            self.nav.nuevo_trayecto(m.ahora)

        vr = vl = 0
        if self.objetivo is not None:
            vr, vl, self.estado, fin = self.nav.paso(m, self.objetivo, self.inicio)
            if fin:
                self.objetivo = None
        self.rastro.actualizar(m.x, m.y, m.theta)
        return vr, vl

    def linea_consola(self, m):
        grados = math.degrees(normalizar(m.theta))
        return (f"\rx = {m.x / 1000:7.3f} m   y = {m.y / 1000:7.3f} m   θ = {grados:7.1f}°   "
                f"{self.estado:<{self.ancho_estado}}")

    def estado_web(self, args):
        datos = self.rastro.para_web(args)
        datos.update(objetivo=self.objetivo, inicio=self.inicio, estado=self.estado,
                     modo=self.texto_modo, choques=self.nav.choques, ir=self.ir,
                     obstaculos=self.nav.obstaculos, encuentros=self.nav.encuentros,
                     salidas=self.nav.salidas)
        return datos

    def acciones_web(self):
        return {"/objetivo": self.poner_objetivo, "/cmd": self.comando}

    def poner_objetivo(self, args):
        # la web envía metros
        self.objetivo = (float(args["x"]) * 1000, float(args["y"]) * 1000)
        self.nuevo = True

    def comando(self, args):
        c = args.get("c", "")
        if c == "p":
            self.objetivo = None
            self.estado = "Parado"
        elif c == "q":
            self.salir = True
