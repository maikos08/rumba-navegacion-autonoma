"""
Modo "parar": va recto al objetivo; si los light bumpers detectan algo delante se para en
seco y espera. Cuando el obstáculo se aparta continúa el camino.
"""
from rumba.modos.base import Modo, frente_ir


class Parar(Modo):
    def iniciar(self, ahora):
        super().iniciar(ahora)
        self.parado = False     # detenido por un obstáculo
        self.t_libre = None     # desde cuándo está libre el camino

    def paso(self, nav, m, objetivo, inicio):
        c = self.cfg
        vr, vl, llegado = self.ir_al_objetivo(m, objetivo)
        frente = frente_ir(m.ir)
        bump = m.bump_izq or m.bump_der
        if llegado:
            return 0, 0, self.texto_llegada(objetivo), "llegado"
        if self.parado:
            # Esperar a que el obstáculo se aparte durante ESPERA_LIBRE segundos
            if frente < c.ir_libre and not bump:
                if self.t_libre is None:
                    self.t_libre = m.ahora
                if m.ahora - self.t_libre >= c.espera_libre:
                    self.parado = False
            else:
                self.t_libre = None
            if self.parado:
                return 0, 0, "Obstáculo delante: esperando", None
            return vr, vl, "Camino libre: continuando", None
        if self.fase == "avanzar" and (frente > c.ir_parada or bump):
            # Parada en seco (girar sobre sí mismo sí se permite: el robot es redondo)
            self.parado, self.t_libre = True, None
            return 0, 0, "Obstáculo delante: parado", None
        return vr, vl, self.texto_fase(), None
