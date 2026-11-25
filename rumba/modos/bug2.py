"""
Modo "bug2" (algoritmo Bug2, tema 5):
  1. Va en línea recta al objetivo (línea M: inicio -> objetivo).
  2. Si encuentra un obstáculo guarda el punto de encuentro H y sigue el contorno.
  3. Sigue el contorno hasta cruzar la línea M en un punto más cercano al objetivo que H.
  4. Si da la vuelta completa y vuelve a H, el objetivo es inalcanzable.
"""
import math

from rumba.modos.base import Modo, frente_ir


def distancia_linea(p, a, b):
    """Distancia con signo del punto p a la recta a-b, y parámetro t de la proyección."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    largo = math.hypot(dx, dy) or 1.0
    d = ((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / largo
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (largo * largo)
    return d, t


class Bug2(Modo):
    def iniciar(self, ahora):
        super().iniciar(ahora)
        self.etapa = "ir"            # "ir" (hacia el objetivo) o "contorno" (siguiendo un obstáculo)
        self.t_inicio = ahora
        self.contorno_total = 0.0    # mm recorridos siguiendo paredes en este trayecto
        self.max_lejos_h = 0.0
        self.punto_h = self.dist_h = self.d_linea_ant = None

    def paso(self, nav, m, objetivo, inicio):
        c = self.cfg
        if self.contorno_total > c.contorno_max or m.ahora - self.t_inicio > c.tiempo_max:
            return 0, 0, "Objetivo inalcanzable (límite de recorrido/tiempo)", "fallo"
        if self.etapa == "ir":
            return self.paso_ir(nav, m, objetivo)
        return self.paso_contorno(nav, m, objetivo, inicio)

    def paso_ir(self, nav, m, objetivo):
        c = self.cfg
        vr, vl, llegado = self.ir_al_objetivo(m, objetivo)
        dist_obj = math.hypot(objetivo[0] - m.x, objetivo[1] - m.y)
        obstaculo_delante = self.fase == "avanzar" and frente_ir(m.ir) > c.ir_frente
        if self.fase == "avanzar":
            # Frenar al acercarse a algo, manteniendo la corrección de rumbo
            f = self.factor_ir(m.ir)
            media, dif = (vr + vl) / 2 * f, (vr - vl) / 2
            vr, vl = media + dif, media - dif

        if llegado:
            return 0, 0, self.texto_llegada(objetivo), "llegado"
        if (m.choque or obstaculo_delante) and dist_obj > c.dist_final:
            # Punto de encuentro H: empieza a seguir el contorno
            self.etapa = "contorno"
            self.punto_h, self.dist_h = (m.x, m.y), dist_obj
            nav.encuentros.append(self.punto_h)
            self.max_lejos_h = 0.0
            self.d_linea_ant = None
            self.maniobra = None
            if m.choque:
                self.iniciar_retroceso(m)
            return 0, 0, "Obstáculo: siguiendo contorno", None
        return vr, vl, self.texto_fase(), None

    def paso_contorno(self, nav, m, objetivo, inicio):
        c = self.cfg
        self.contorno_total += abs(m.ds)
        dist_obj = math.hypot(objetivo[0] - m.x, objetivo[1] - m.y)
        d_linea, t = distancia_linea((m.x, m.y), inicio, objetivo)
        cruza = abs(d_linea) < c.tol_linea or (
            self.d_linea_ant is not None and d_linea * self.d_linea_ant < 0)
        self.d_linea_ant = d_linea
        lejos_h = math.hypot(m.x - self.punto_h[0], m.y - self.punto_h[1])
        self.max_lejos_h = max(self.max_lejos_h, lejos_h)

        if m.choque:
            self.iniciar_retroceso(m)

        if self.maniobra is None and cruza and 0 <= t <= 1 \
                and dist_obj < self.dist_h - c.mejora and lejos_h > c.sep_h \
                and frente_ir(m.ir) < c.ir_lento:
            # Vuelve a la línea M más cerca del objetivo -> deja el contorno
            self.etapa, self.fase = "ir", "girar"
            nav.salidas.append((m.x, m.y))
            return 0, 0, "Línea M alcanzada: hacia el objetivo", None
        if self.maniobra is None and self.max_lejos_h > c.lejos_h and lejos_h < c.radio_h:
            # Ha rodeado el obstáculo (o la habitación) entero sin encontrar salida
            return 0, 0, "Objetivo inalcanzable (vuelta completa)", "fallo"
        maniobra = self.maniobra_choque(m)
        if maniobra:
            vr, vl, estado = maniobra
            return vr, vl, estado, None
        vr, vl = self.seguir_contorno(m.ir)
        lado = "derecha)" if self.cfg.lado > 0 else "izquierda)"
        return vr, vl, "Siguiendo contorno (obstáculo a la " + lado, None
