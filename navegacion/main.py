"""Navegación a un punto con odometría (giro + avance). Ver README.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto

from rumba.ejecutar import lanzar              # noqa: E402
from rumba.navegacion import TareaObjetivo     # noqa: E402

PAGINA = Path(__file__).resolve().parent / "ui.html"


def main(robot=None):
    # modo "directo": va recto al objetivo y, si choca, lo cancela
    lanzar(lambda cfg: TareaObjetivo(cfg, "directo", PAGINA), robot=robot)


if __name__ == "__main__":
    main()
