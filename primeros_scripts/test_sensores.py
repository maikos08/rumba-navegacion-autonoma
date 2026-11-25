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

try:
    for i in range(600):  # ~5 min
        s = bot.get_sensors()
        lb = (s.light_bumper_left, s.light_bumper_front_left,
              s.light_bumper_center_left, s.light_bumper_center_right,
              s.light_bumper_front_right, s.light_bumper_right)
        print(i, lb, s.battery_charge, "/", s.battery_capacity)
        if max(lb) > 4095:
            print("¡Valor fuera de rango!")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    bot.drive_stop()
    bot.close()
