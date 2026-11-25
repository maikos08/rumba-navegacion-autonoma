"""
Todo lo que toca el robot: la conexión (Robot), la odometría (Odometria) y el rastro
que se dibuja en la web (Rastro). Es el ÚNICO archivo que importa pycreate2.
La odometría está explicada en docs/odometria.md.
"""
import math
import time
from types import SimpleNamespace


class Robot:
    def __init__(self, puerto, fabrica=None):
        if fabrica is None:
            from pycreate2 import Create2 as fabrica
        self.bot = fabrica(puerto)

    def conectar(self):
        self.bot.start()
        self.bot.safe()

    def leer(self, intentos=3):
        """get_sensors() con reintento (a veces el robot no responde) y con lo que usamos."""
        for _ in range(intentos):
            try:
                s = self.bot.get_sensors()
                break
            except Exception:
                self.bot.start()
                self.bot.safe()
                time.sleep(0.1)
        else:
            raise RuntimeError("El robot no responde")

        bw = s.bumps_wheeldrops
        campo_oi = next((f for f in s._fields if "mode" in f), None)
        return SimpleNamespace(
            enc_l=s.encoder_counts_left,
            enc_r=s.encoder_counts_right,
            # (left, front_left, center_left, center_right, front_right, right)
            ir=(s.light_bumper_left, s.light_bumper_front_left, s.light_bumper_center_left,
                s.light_bumper_center_right, s.light_bumper_front_right, s.light_bumper_right),
            bump_izq=bool(getattr(bw, "bump_left", False)),
            bump_der=bool(getattr(bw, "bump_right", False)),
            oi_modo=getattr(s, campo_oi, None) if campo_oi else None,   # 1 = Passive, 2 = Safe
        )

    def mover(self, vr, vl):
        """Velocidades de rueda derecha / izquierda en mm/s."""
        self.bot.drive_direct(int(round(vr)), int(round(vl)))

    def reactivar(self):
        """Start + Safe: devuelve el robot a modo Safe (p. ej. tras levantarlo del suelo)."""
        self.bot.start()
        self.bot.safe()

    def cerrar(self):
        try:
            self.bot.drive_stop()
            self.bot.start()   # vuelve a modo pasivo (la spec lo recomienda para proteger la batería)
        except Exception:
            pass
        self.bot.close()


class Odometria:
    """Posición (x, y en mm, theta en rad) a partir de los encoders. Origen: donde arranca."""

    def __init__(self, cfg):
        self.b = cfg.b
        self.mm_por_cuenta = cfg.mm_por_cuenta
        self.x = self.y = self.theta = 0.0
        self.enc_l = self.enc_r = None

    def iniciar(self, enc_l, enc_r):
        self.enc_l, self.enc_r = enc_l, enc_r

    def reiniciar_pose(self):
        self.x = self.y = self.theta = 0.0

    def actualizar(self, enc_l, enc_r):
        """Devuelve (ds, dtheta): avance (mm) y giro (rad) desde la lectura anterior."""
        ds_l = self._delta(enc_l, self.enc_l) * self.mm_por_cuenta
        ds_r = self._delta(enc_r, self.enc_r) * self.mm_por_cuenta
        self.enc_l, self.enc_r = enc_l, enc_r

        ds = (ds_r + ds_l) / 2
        dtheta = (ds_r - ds_l) / self.b
        self.x += ds * math.cos(self.theta + dtheta)
        self.y += ds * math.sin(self.theta + dtheta)
        self.theta += dtheta
        return ds, dtheta

    @staticmethod
    def _delta(nuevo, anterior):
        """Diferencia de encoder teniendo en cuenta el desbordamiento de 16 bits."""
        return (nuevo - anterior + 32768) % 65536 - 32768


class Rastro:
    """Pose actual y puntos recorridos, para dibujarlos en la web."""

    def __init__(self, min_paso):
        self.min_paso = min_paso
        self.pose = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.camino = [(0.0, 0.0)]
        self.rev = 0     # sube cuando se borra el rastro: la web se entera y lo redibuja

    def actualizar(self, x, y, theta):
        self.pose.update(x=x, y=y, theta=theta)
        ux, uy = self.camino[-1]
        if math.hypot(x - ux, y - uy) >= self.min_paso:
            self.camino.append((x, y))

    def borrar(self, origen):
        self.camino[:] = [origen]
        self.rev += 1

    def para_web(self, args):
        """Pose + puntos nuevos desde args['desde']."""
        desde = int(args.get("desde", 0))
        if int(args.get("rev", -1)) != self.rev:
            desde = 0   # la web tiene un rastro antiguo: se le manda entero
        return dict(self.pose, nuevos=self.camino[desde:], rev=self.rev)
