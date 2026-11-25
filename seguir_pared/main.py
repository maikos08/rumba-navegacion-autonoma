"""Exploración reactiva: busca una pared y la sigue. Ver README.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # raíz del proyecto

from rumba.ejecutar import lanzar                   # noqa: E402
from rumba.exploracion import TareaExploracion      # noqa: E402


def main(robot=None):
    lanzar(lambda cfg: TareaExploracion(cfg, "seguir_pared", "seguir pared"), robot=robot)


if __name__ == "__main__":
    main()
