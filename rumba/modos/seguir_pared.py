"""
Modo "seguir_pared" (seguirpared): exploración reactiva sin mapa, al estilo de los algoritmos BUG.

  1. BUSCAR: avanza recto, frenando al acercarse a algo, hasta encontrar una pared
     (IR frontal o lateral, o parachoques).
  2. SEGUIR: la sigue manteniendo IR_OBJETIVO en el sensor lateral (pared a la izquierda si
     LADO=-1, a la derecha si LADO=+1). Rodea las esquinas exteriores, gira en las interiores
     y, si choca, retrocede y se aparta. Es el mismo seguimiento que usa Bug2.
  3. Si pierde la pared durante PARED_PERDIDA_TIEMPO segundos (espacio abierto), vuelve a BUSCAR.
"""
from rumba.modos.base import Modo, frente_ir


class SeguirPared(Modo):
    def iniciar(self, ahora):
        super().iniciar(ahora)
        self.etapa = "buscar"     # "buscar" o "seguir"
        self.t_perdida = None     # desde cuándo no ve la pared

    def paso(self, nav, m, objetivo, inicio):
        c = self.cfg
        ir = m.ir
        lateral = max(ir[0], ir[1]) if c.lado < 0 else max(ir[4], ir[5])
        frente = frente_ir(ir)
        bump = m.bump_izq or m.bump_der

        if self.etapa == "buscar":
            if bump or frente > c.ir_frente or lateral >= c.ir_perdida:
                self.etapa, self.t_perdida, self.maniobra = "seguir", None, None
                if m.choque:
                    self.iniciar_retroceso(m)
                return 0, 0, "Pared encontrada", None
            v = c.v_avance * self.factor_ir(ir)    # frena si algo se acerca por delante
            return v, v, "Buscando pared", None

        # etapa "seguir"
        if lateral < c.ir_perdida and frente <= c.ir_frente:
            if self.t_perdida is None:
                self.t_perdida = m.ahora
            elif m.ahora - self.t_perdida > c.pared_perdida_tiempo:
                self.etapa = "buscar"
                return 0, 0, "Pared perdida: buscando otra", None
        else:
            self.t_perdida = None

        if m.choque:
            self.iniciar_retroceso(m)
        maniobra = self.maniobra_choque(m)
        if maniobra:
            vr, vl, estado = maniobra
            return vr, vl, estado, None
        vr, vl = self.seguir_contorno(ir)
        lado = "derecha)" if c.lado > 0 else "izquierda)"
        return vr, vl, "Siguiendo pared (a la " + lado, None
