"""Navegación a un punto evitando obstáculos (parar o Bug2). Ver README.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto

from rumba.ejecutar import lanzar                         # noqa: E402
from rumba.navegacion import TareaObjetivo, elegir_modo   # noqa: E402

PAGINA = Path(__file__).resolve().parent / "ui.html"


def crear_tarea(cfg):
    modo, texto = elegir_modo()     # "parar" o "bug2"
    return TareaObjetivo(cfg, modo, PAGINA, texto_modo=texto, ancho_estado=45)


def main(robot=None):
    lanzar(crear_tarea, robot=robot)


if __name__ == "__main__":
    main()
