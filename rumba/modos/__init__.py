"""Modos de navegación: un archivo por modo. Para añadir uno, crea el archivo y regístralo aquí."""
from rumba.modos.bug2 import Bug2
from rumba.modos.directo import Directo
from rumba.modos.limpieza import Limpieza
from rumba.modos.parar import Parar
from rumba.modos.seguir_pared import SeguirPared

MODOS = {
    "directo": Directo,              # ir a un punto, sin sensores
    "parar": Parar,                  # ir a un punto, parando ante obstáculos
    "bug2": Bug2,                    # ir a un punto, rodeando obstáculos
    "limpieza": Limpieza,            # sin objetivo: recorrer la habitación al azar (chocayvuelve)
    "seguir_pared": SeguirPared,     # sin objetivo: explorar siguiendo paredes (seguirpared)
}
