"""Funciones matemáticas sencillas que usan varios scripts."""
import math


def normalizar(a):
    """Ángulo en (-pi, pi]."""
    return math.atan2(math.sin(a), math.cos(a))


def limitar(v, vmin, vmax):
    return max(vmin, min(vmax, v))


def girar_hacia(signo, w):
    """Giro sobre sí mismo: signo +1 izquierda (antihorario), -1 derecha. Devuelve (vr, vl)."""
    return signo * w, -signo * w
