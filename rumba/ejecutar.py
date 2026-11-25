"""
Arranque y bucle principal, iguales para todas las tareas.

Una tarea es una clase que hereda de `Tarea` y define:
    paso(m)              -> (vr, vl) velocidades de rueda en mm/s, o None para terminar
    estado_web(args)     -> dict con lo que pinta la web
    acciones_web()       -> {"/ruta": funcion(args)} para los botones de la web
    linea_consola(m)     -> texto de la consola
    pagina               -> ruta del ui.html
`m` trae la pose (x, y, theta), el avance del paso (ds, dtheta), los sensores
(ir, bump_izq, bump_der, choque, oi_modo) y la hora (ahora).
Si una tarea pone self.reactivar = True, el bucle hace Start + Safe al robot.
"""
import threading
import time
from types import SimpleNamespace

from rumba.config import cargar_config
from rumba.robot import Odometria, Robot
from rumba.servidor import ServidorWeb


class Tarea:
    reactivar = False

    def __init__(self):
        # El servidor web y el bucle del robot corren en hilos distintos: este lock
        # evita que se lean/escriban los datos de la tarea a la vez.
        self.lock = threading.Lock()


def lanzar(crear_tarea, robot=None):
    """crear_tarea(cfg) -> Tarea. `robot` solo se pasa en las pruebas (robot simulado)."""
    cfg = cargar_config()
    tarea = crear_tarea(cfg)     # antes de conectar: puede hacer preguntas por consola

    try:
        robot = robot or Robot(cfg.puerto)
        robot.conectar()
    except Exception as e:
        raise SystemExit(
            f"No se pudo conectar con el robot en {cfg.puerto} ({type(e).__name__}).\n"
            "Comprueba que está encendido y conectado por USB, que el puerto es el correcto "
            "(PUERTO en config.env) y que ningún otro programa lo usa.")

    servidor = ServidorWeb(tarea, cfg.http_host, cfg.http_port)
    servidor.iniciar(cfg.abrir_navegador)
    print(f"Mapa en {servidor.url}")

    odo = Odometria(cfg)
    s = robot.leer()
    odo.iniciar(s.enc_l, s.enc_r)
    bump_ant = False
    try:
        while True:
            # 1. Sensores y odometría
            s = robot.leer()
            ds, dtheta = odo.actualizar(s.enc_l, s.enc_r)
            bump = s.bump_izq or s.bump_der
            m = SimpleNamespace(x=odo.x, y=odo.y, theta=odo.theta, ds=ds, dtheta=dtheta,
                                ir=s.ir, bump_izq=s.bump_izq, bump_der=s.bump_der,
                                choque=bump and not bump_ant,    # flanco: acaba de pulsarse
                                oi_modo=s.oi_modo, ahora=time.time(), odometria=odo)
            bump_ant = bump

            # 2. La tarea decide
            with tarea.lock:
                orden = tarea.paso(m)
                reactivar, tarea.reactivar = tarea.reactivar, False
            if orden is None:
                break

            # 3. Mover el robot
            if reactivar:
                # Si el robot se levantó o detectó un desnivel, el OI pasó solo a modo Passive
                # e ignora las órdenes: Start + Safe lo devuelven a Safe.
                robot.reactivar()
                time.sleep(0.05)
                orden = (0, 0)
            # Se reenvía siempre: si una lectura falla y se reinicia el modo safe,
            # el robot recupera el movimiento en la siguiente iteración.
            robot.mover(*orden)

            print(tarea.linea_consola(m), end="", flush=True)
            time.sleep(cfg.periodo)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nParando robot")
        robot.cerrar()
        servidor.detener()
