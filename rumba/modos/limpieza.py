"""
Modo "limpieza" (chocayvuelve): recorre una habitación sin objetivo, como una aspiradora.

  - Avanza en línea recta, frenando al acercarse a algo (light bumpers).
  - Ante un obstáculo (IR frontal o parachoques) lo evita y continúa: si chocó retrocede
    un poco; después gira un ángulo AL AZAR (entre LIMPIEZA_ANG_MIN y LIMPIEZA_ANG_MAX
    grados, a izquierda o derecha) y sigue recto. Así cada pasada sale en una dirección
    distinta y no se repite el recorrido.
  - No se queda atascado: si choca varias veces seguidas sin avanzar, o en ATASCO_TIEMPO
    segundos se ha movido menos de ATASCO_DIST mm, hace una maniobra de escape
    (retrocede más y da casi media vuelta).
"""
import math
import random

from rumba.geometria import girar_hacia, limitar
from rumba.modos.base import Modo, frente_ir


class Limpieza(Modo):
    def __init__(self, cfg):
        self.azar = random.Random(cfg.semilla or None)   # SEMILLA=0 -> distinto en cada ejecución
        super().__init__(cfg)

    def iniciar(self, ahora):
        super().iniciar(ahora)
        self.etapa = "avanzar"        # "avanzar", "retroceder" o "girar"
        self.retro_mm = 0.0           # lo que debe retroceder
        self.x0 = self.y0 = 0.0       # donde empezó a retroceder
        self.resto = 0.0              # rad que faltan por girar
        self.choques_seguidos = 0     # choques sin haber recorrido LIMPIEZA_LIBRE mm
        self.recorrido_libre = 0.0
        self.ref = None               # (x, y, hora) para detectar que no avanza
        self.escape = False           # la maniobra en curso es de escape

    def paso(self, nav, m, objetivo, inicio):
        c = self.cfg
        if self.ref is None:
            self.ref = (m.x, m.y, m.ahora)

        # ¿Atascado? Casi no se ha movido en ATASCO_TIEMPO segundos
        if m.ahora - self.ref[2] > c.atasco_tiempo:
            movido = math.hypot(m.x - self.ref[0], m.y - self.ref[1])
            self.ref = (m.x, m.y, m.ahora)
            if movido < c.atasco_dist and not self.escape:
                self.empezar_retroceso(m, 2 * c.limpieza_retro, escape=True)

        if self.etapa == "avanzar":
            return self.avanzar(m)
        if self.etapa == "retroceder":
            return self.retroceder(m)
        return self.girar(m)

    def avanzar(self, m):
        c = self.cfg
        if m.bump_izq or m.bump_der:
            self.choques_seguidos += 1
            self.empezar_retroceso(m, c.limpieza_retro)
            return 0, 0, "Choque: retrocediendo", None
        if frente_ir(m.ir) > c.ir_frente:
            self.choques_seguidos += 1
            self.empezar_giro(m)
            return 0, 0, "Obstáculo delante: girando", None
        self.recorrido_libre += abs(m.ds)
        if self.recorrido_libre > c.limpieza_libre:
            self.choques_seguidos = 0
        v = c.v_avance * self.factor_ir(m.ir)    # frena si algo se acerca por delante
        return v, v, "Limpiando: avanzando", None

    def retroceder(self, m):
        if math.hypot(m.x - self.x0, m.y - self.y0) >= self.retro_mm:
            self.empezar_giro(m)
            return 0, 0, "Girando", None
        return -self.cfg.v_contorno, -self.cfg.v_contorno, "Retrocediendo", None

    def girar(self, m):
        c = self.cfg
        self.resto -= m.dtheta
        if abs(self.resto) < c.tol_giro:
            self.etapa, self.escape = "avanzar", False
            self.recorrido_libre = 0.0
            self.ref = (m.x, m.y, m.ahora)
            return 0, 0, "Limpiando: avanzando", None
        w = limitar(c.k_giro * abs(self.resto), c.v_giro_min, c.v_giro)
        vr, vl = girar_hacia(1 if self.resto > 0 else -1, w)
        return vr, vl, f"Girando: faltan {math.degrees(self.resto):.0f}°", None

    def empezar_retroceso(self, m, mm, escape=False):
        self.etapa = "retroceder"
        self.retro_mm = mm
        self.x0, self.y0 = m.x, m.y
        self.escape = escape

    def empezar_giro(self, m):
        """Elige un ángulo al azar. Con muchos choques seguidos o atascado, casi media vuelta."""
        c = self.cfg
        if self.escape or self.choques_seguidos >= c.limpieza_choques_atasco:
            grados = 180 + self.azar.uniform(-30, 30)
            self.choques_seguidos = 0
            self.escape = True
        else:
            grados = self.azar.uniform(c.limpieza_ang_min_grados, c.limpieza_ang_max_grados)
        self.resto = math.radians(grados) * self.azar.choice((-1, 1))
        self.etapa = "girar"
