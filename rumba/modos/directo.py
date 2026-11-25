"""Modo "directo": va recto al objetivo sin mirar los sensores de proximidad. Si choca, lo cancela."""
from rumba.modos.base import Modo


class Directo(Modo):
    def paso(self, nav, m, objetivo, inicio):
        if m.bump_izq or m.bump_der:
            return 0, 0, "Choque: objetivo cancelado", "cancelado"
        vr, vl, llegado = self.ir_al_objetivo(m, objetivo)
        if llegado:
            return vr, vl, self.texto_llegada(objetivo), "llegado"
        return vr, vl, self.texto_fase(), None
