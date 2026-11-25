"""
Circuito: cola de instrucciones ("Ir a" y "Girar") que el robot ejecuta en orden.
Cada "Ir a" usa el modo elegido (parar o rodear con Bug2). Ver README.md.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto

from rumba.ejecutar import Tarea, lanzar                       # noqa: E402
from rumba.geometria import girar_hacia, limitar, normalizar     # noqa: E402
from rumba.navegacion import Navegador, elegir_modo              # noqa: E402
from rumba.robot import Rastro                                   # noqa: E402


class Circuito(Tarea):
    pagina = Path(__file__).resolve().parent / "ui.html"

    def __init__(self, cfg, modo, texto_modo):
        super().__init__()
        self.cfg = cfg
        self.rastro = Rastro(cfg.min_paso)
        self.nav = Navegador(cfg, modo)
        self.texto_modo = texto_modo

        self.cola = []              # [{"tipo": "ir", "x", "y"} | {"tipo": "girar", "grados"}]
        self.indice = 0             # instrucción en curso
        self.ejecutando = False
        self.repetir = False
        self.objetivo = None        # "Ir a" en curso (mm)
        self.inicio = None
        self.giro = None            # rad que faltan de la instrucción "Girar" en curso
        self.estado = "Añade instrucciones en la página"
        self.ir = [0] * 6
        self.oi_modo = None         # 0 off, 1 passive, 2 safe, 3 full
        # Peticiones de los botones que atiende el bucle del robot
        self.salir = self.borrar_mapa = self.reiniciar = False

    # ---------- Bucle del robot ----------
    def paso(self, m):
        c = self.cfg
        x, y, theta = m.x, m.y, m.theta
        self.ir = list(m.ir)
        self.oi_modo = m.oi_modo
        if self.salir:
            return None

        reactivar = False
        if self.reiniciar:
            # Nuevo origen donde esté ahora el robot y vuelta a modo Safe
            self.reiniciar = False
            m.odometria.reiniciar_pose()
            x, y, theta = 0.0, 0.0, 0.0
            self.rastro.borrar((0.0, 0.0))
            self.nav.borrar_mapa()
            self.ejecutando = False
            self.indice = 0
            self.cancelar_actual()
            self.nav.nuevo_trayecto(m.ahora)
            self.estado = "Origen reiniciado (0, 0, 0°) y modo Safe"
            reactivar = True
            self.reactivar = True
        if self.borrar_mapa:
            self.borrar_mapa = False
            self.rastro.borrar((x, y))
            self.nav.borrar_mapa()

        # Instrucción "Girar": se descuenta lo girado según la odometría
        if self.giro is not None:
            self.giro -= m.dtheta

        # Cargar la siguiente instrucción de la cola
        if self.ejecutando and self.objetivo is None and self.giro is None:
            if self.indice < len(self.cola):
                it = self.cola[self.indice]
                if it["tipo"] == "ir":
                    self.objetivo = (it["x"], it["y"])
                    self.inicio = (x, y)
                    self.nav.nuevo_trayecto(m.ahora)
                else:
                    self.giro = math.radians(it["grados"])
            else:
                self.ejecutando = False

        vr = vl = 0
        if self.giro is not None:
            resto = self.giro
            if abs(resto) < c.tol_giro:
                self.terminar_instruccion(True, f"Giro completado (θ = {math.degrees(normalizar(theta)):.1f}°)")
            else:
                w = limitar(c.k_giro * abs(resto), c.v_giro_min, c.v_giro)
                vr, vl = girar_hacia(1 if resto > 0 else -1, w)
                self.estado = f"Girando: faltan {math.degrees(resto):.1f}°"
        elif self.objetivo is not None:
            vr, vl, estado, fin = self.nav.paso(m, self.objetivo, self.inicio)
            if fin is None:
                self.estado = estado
            else:
                self.terminar_instruccion(fin == "llegado", estado)

        if m.oi_modo == 1 and not reactivar:
            self.estado = "Modo Passive: el robot no obedece (pulsa Reiniciar)"

        self.rastro.actualizar(x, y, theta)
        return vr, vl

    def cancelar_actual(self):
        """Deja de ejecutar la instrucción en curso."""
        self.objetivo = None
        self.giro = None

    def terminar_instruccion(self, ok, estado):
        """
        Cierra la instrucción en curso.
        ok=True: pasa a la siguiente (o vuelve a empezar si 'repetir'); ok=False: detiene la cola.
        """
        self.cancelar_actual()
        self.estado = estado
        if not self.ejecutando:
            return
        if not ok:
            self.ejecutando = False
            return
        self.indice += 1
        if self.indice >= len(self.cola):
            if self.repetir and self.cola:
                self.indice = 0
            else:
                self.ejecutando = False
                self.estado = estado + " · Circuito completado"

    def linea_consola(self, m):
        grados = math.degrees(normalizar(m.theta))
        return (f"\rx = {m.x / 1000:7.3f} m   y = {m.y / 1000:7.3f} m   θ = {grados:7.1f}°   "
                f"{self.estado:<45}")

    # ---------- Web ----------
    def estado_web(self, args):
        datos = self.rastro.para_web(args)
        datos.update(objetivo=self.objetivo, inicio=self.inicio, estado=self.estado,
                     modo=self.texto_modo, choques=self.nav.choques, ir=self.ir,
                     cola=self.cola, indice=self.indice, ejecutando=self.ejecutando,
                     repetir=self.repetir, giro_restante=self.giro, oi_modo=self.oi_modo,
                     obstaculos=self.nav.obstaculos, encuentros=self.nav.encuentros,
                     salidas=self.nav.salidas)
        return datos

    def acciones_web(self):
        return {"/cola/add": self.anadir, "/cola/del": self.quitar, "/cola/subir": self.subir,
                "/cola/limpiar": self.limpiar, "/cmd": self.comando}

    def anadir(self, args):
        tipo = args.get("tipo")
        if tipo == "ir":
            self.cola.append({"tipo": "ir", "x": float(args["x"]) * 1000, "y": float(args["y"]) * 1000})
        elif tipo == "girar":
            self.cola.append({"tipo": "girar", "grados": float(args["g"])})
        else:
            raise ValueError(tipo)

    def quitar(self, args):
        i = int(args.get("i", -1))
        if 0 <= i < len(self.cola):
            self.cola.pop(i)
            if i < self.indice:
                self.indice -= 1
            elif i == self.indice:
                self.cancelar_actual()   # se borra la que está en curso: pasa a la siguiente

    def subir(self, args):
        i = int(args.get("i", -1))
        if 1 <= i < len(self.cola):
            self.cola[i - 1], self.cola[i] = self.cola[i], self.cola[i - 1]
            if self.indice in (i - 1, i):
                self.cancelar_actual()   # cambia la instrucción en curso: se recarga

    def limpiar(self, args):
        self.cola.clear()
        self.indice = 0
        self.ejecutando = False
        self.cancelar_actual()
        self.estado = "Cola vacía"

    def comando(self, args):
        c = args.get("c", "")
        if c == "ejecutar" and self.cola:
            if self.indice >= len(self.cola):
                self.indice = 0
            self.ejecutando = True
        elif c == "parar":
            self.ejecutando = False
            self.cancelar_actual()
            self.estado = "Parado"
        elif c == "repetir":
            self.repetir = args.get("v") == "1"
        elif c == "borrar_mapa":
            self.borrar_mapa = True
        elif c == "reiniciar":
            self.reiniciar = True
        elif c == "q":
            self.salir = True


def crear_tarea(cfg):
    modo, texto = elegir_modo()     # "parar" o "bug2"
    return Circuito(cfg, modo, texto)


def main(robot=None):
    lanzar(crear_tarea, robot=robot)


if __name__ == "__main__":
    main()
