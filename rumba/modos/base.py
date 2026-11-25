"""
Lo que comparten los tres modos de navegación: ir al objetivo girando y avanzando.
y el seguimiento de pared con los light bumpers (lo usan bug2.py y seguir_pared.py).
Cada modo hereda de `Modo` y solo añade lo suyo.

Un modo tiene dos métodos:
    iniciar(ahora)                    reinicia su estado para un trayecto nuevo
    paso(nav, m, objetivo, inicio)    devuelve (vr, vl, estado, fin)
                                      fin = None | "llegado" | "fallo" | "cancelado"
`nav` es el Navegador (guarda choques y marcas del mapa) y `m` los datos del ciclo.
Los modos que no van a un objetivo (limpieza, seguir_pared) reciben objetivo = None.
"""
import math

from rumba.geometria import girar_hacia, limitar, normalizar


def frente_ir(ir):
    """Lectura delantera: sensores centrales y, con algo menos de peso, los frontales laterales."""
    return max(ir[2], ir[3], 0.7 * ir[1], 0.7 * ir[4])


class Modo:
    def __init__(self, cfg):
        self.cfg = cfg
        self.iniciar(0.0)

    def iniciar(self, ahora):
        self.fase = "girar"     # "girar" o "avanzar"
        self.maniobra = None    # retroceder / apartarse tras un choque (ver maniobra_choque)

    def ir_al_objetivo(self, m, objetivo):
        """
        Ir al objetivo en línea recta. Devuelve (vr, vl, llegado) y actualiza self.fase.
        Fase "girar": gira sobre sí mismo hasta apuntar al objetivo.
        Fase "avanzar": avanza corrigiendo el rumbo; si el error crece, vuelve a girar.
        """
        c = self.cfg
        dx, dy = objetivo[0] - m.x, objetivo[1] - m.y
        dist = math.hypot(dx, dy)
        if dist < c.tol_dist:
            self.fase = "girar"
            return 0, 0, True

        error = normalizar(math.atan2(dy, dx) - m.theta)   # >0: objetivo a la izquierda

        # Tramo final: cerca del objetivo un pequeño desvío lateral da errores de ángulo
        # grandes, así que no se vuelve a girar; si el objetivo ya queda detrás, se ha llegado.
        if self.fase == "avanzar" and dist < c.dist_final:
            if abs(error) > math.pi / 2:
                self.fase = "girar"
                return 0, 0, True
            v = limitar(dist, c.v_avance_min, c.v_avance)
            return v, v, False

        if self.fase == "avanzar" and abs(error) > c.ang_max:
            self.fase = "girar"
        elif self.fase == "girar" and abs(error) < c.ang_ok:
            self.fase = "avanzar"

        if self.fase == "girar":
            w = limitar(c.k_giro * abs(error), c.v_giro_min, c.v_giro)
            vr, vl = girar_hacia(1 if error > 0 else -1, w)
            return vr, vl, False

        v = limitar(dist, c.v_avance_min, c.v_avance)   # frena al acercarse
        corr = c.k_corr * error
        return v + corr, v - corr, False

    def factor_ir(self, ir):
        """1 si no hay nada delante; baja hasta FACTOR_MIN al acercarse a IR_FRENTE."""
        c = self.cfg
        f = (c.ir_frente - frente_ir(ir)) / (c.ir_frente - c.ir_lento)
        return limitar(f, c.factor_min, 1.0)

    def seguir_contorno(self, ir):
        """
        Seguimiento de pared con los light bumpers. Devuelve (vr, vl).
        c.lado = +1: pared a la derecha (se aparta girando a la izquierda); -1: a la izquierda.
        ir = (left, front_left, center_left, center_right, front_right, right)
        """
        c = self.cfg
        aparta = c.lado   # signo de giro que aleja del obstáculo (+1 izquierda)
        lateral = max(ir[4], ir[5]) if c.lado > 0 else max(ir[0], ir[1])

        if frente_ir(ir) > c.ir_frente:
            # Pared delante (esquina interior): girar sobre sí mismo para alejarse.
            # El robot es redondo, así que puede girar sin tocar la pared.
            return girar_hacia(aparta, c.v_giro_min * 1.5)

        v = c.v_contorno * self.factor_ir(ir)   # frena si algo se acerca por delante
        if lateral < c.ir_perdida:
            # Pared perdida (esquina exterior o puerta): arco lento hacia la pared para rodearla
            v = min(v, c.v_buscar)
            return v - aparta * c.v_arco, v + aparta * c.v_arco
        # Mantener distancia: demasiado cerca -> apartarse, demasiado lejos -> acercarse
        corr = limitar(c.k_pared * (lateral - c.ir_objetivo), -c.corr_max, c.corr_max)
        return v + aparta * corr, v - aparta * corr

    def iniciar_retroceso(self, m):
        """Tras un choque: retrocede un poco y luego gira para apartarse (ver maniobra_choque)."""
        self.maniobra = {"tipo": "retroceder", "x0": m.x, "y0": m.y}

    def maniobra_choque(self, m):
        """
        Si hay una maniobra de choque en curso devuelve (vr, vl, estado), si no None.
        Retrocede RETRO_CONTORNO mm y después gira ANG_APARTARSE hacia el lado contrario a la pared.
        """
        c = self.cfg
        if self.maniobra is None:
            return None
        if self.maniobra["tipo"] == "retroceder":
            if math.hypot(m.x - self.maniobra["x0"], m.y - self.maniobra["y0"]) >= c.retro_contorno:
                self.maniobra = {"tipo": "apartarse", "th0": m.theta}
                vr, vl = 0, 0
            else:
                vr, vl = -c.v_contorno, -c.v_contorno
            return vr, vl, "Contorno: retrocediendo"
        # apartarse
        if abs(normalizar(m.theta - self.maniobra["th0"])) >= c.ang_apartarse:
            self.maniobra = None
            vr, vl = 0, 0
        else:
            vr, vl = girar_hacia(c.lado, c.v_giro)
        return vr, vl, "Contorno: apartándose"

    def texto_fase(self):
        return "Girando" if self.fase == "girar" else "Avanzando"

    @staticmethod
    def texto_llegada(objetivo):
        return f"Llegado a ({objetivo[0] / 1000:.2f}, {objetivo[1] / 1000:.2f}) m"
