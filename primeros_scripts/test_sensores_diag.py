import sys
import time
from pathlib import Path

from pycreate2 import Create2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto
from core.config import cargar_config  # noqa: E402

PUERTO = cargar_config().puerto   # se cambia en config.env

bot = Create2(PUERTO)
bot.start()
bot.safe()

t0 = time.time()
fallos = 0

try:
    for i in range(600):  # ~5 min
        try:
            s = bot.get_sensors()
        except Exception as e:
            fallos += 1
            print(f"[{time.time() - t0:6.1f} s] FALLO {fallos}: {e}")

            # Ver si el robot ha mandado algo de texto (p. ej. mensajes de reinicio)
            ser = getattr(bot.SCI, "ser", None)
            if ser is not None:
                time.sleep(0.5)
                pendiente = ser.read(ser.in_waiting or 1)
                print("   bytes pendientes en el puerto:", pendiente)

            # Reintentar: volver a arrancar la interfaz del robot
            bot.start()
            bot.safe()
            time.sleep(0.5)
            continue

        lb = (s.light_bumper_left, s.light_bumper_front_left,
              s.light_bumper_center_left, s.light_bumper_center_right,
              s.light_bumper_front_right, s.light_bumper_right)
        campo_modo = next((f for f in s._fields if "mode" in f), None)
        modo = getattr(s, campo_modo) if campo_modo else "?"
        print(f"[{time.time() - t0:6.1f} s] {i} {lb} {s.battery_charge}/{s.battery_capacity} modo={modo}")
        if max(lb) > 4095:
            print("¡Valor fuera de rango!")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    print(f"Fallos totales: {fallos}")
    try:
        bot.drive_stop()
    except Exception:
        pass
    bot.close()