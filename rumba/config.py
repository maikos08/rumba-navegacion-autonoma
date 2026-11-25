"""
Lee config.env y lo devuelve como un objeto: cfg.v_avance, cfg.puerto, cfg.ang_ok...
config.env es la única fuente de valores. Una variable de entorno RUMBA_<CLAVE>
(p. ej. set RUMBA_PUERTO=COM7) tiene prioridad sobre el archivo.
"""
import math
import os
from pathlib import Path
from types import SimpleNamespace

RUTA = Path(__file__).resolve().parent.parent / "config.env"


def _convertir(texto):
    for tipo in (int, float):
        try:
            return tipo(texto)
        except ValueError:
            pass
    return texto


def cargar_config(ruta=RUTA):
    cfg = SimpleNamespace()
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()      # quita comentarios
        if not linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip().lower()
        valor = os.environ.get("RUMBA_" + clave.upper(), valor.strip())
        setattr(cfg, clave, _convertir(valor))

    # Valores derivados (el control trabaja en radianes)
    cfg.mm_por_cuenta = math.pi * cfg.diametro_rueda / cfg.cuentas_por_vuelta
    cfg.ang_ok = math.radians(cfg.ang_ok_grados)
    cfg.ang_max = math.radians(cfg.ang_max_grados)
    cfg.tol_giro = math.radians(cfg.tol_giro_grados)
    cfg.ang_apartarse = math.radians(cfg.ang_apartarse_grados)
    return cfg
