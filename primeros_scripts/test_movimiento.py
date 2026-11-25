import sys
import time
from pathlib import Path

from pycreate2 import Create2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto
from core.config import cargar_config  # noqa: E402

PUERTO = cargar_config().puerto   # se cambia en config.env
VEL = 100  # mm/s (máx. 500)

bot = Create2(PUERTO)
bot.start()
bot.safe()

try:
    print("Adelante 2 s")
    bot.drive_direct(VEL, VEL)
    time.sleep(2)
    bot.drive_stop()
    time.sleep(1)

    print("Giro sobre sí mismo 2 s")
    bot.drive_direct(VEL, -VEL)
    time.sleep(2)
    bot.drive_stop()
    time.sleep(1)

    print("Atrás 2 s")
    bot.drive_direct(-VEL, -VEL)
    time.sleep(2)
    bot.drive_stop()
except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    try:
        bot.drive_stop()
    except Exception:
        pass
    bot.close()
