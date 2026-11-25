# Navegación a un punto (avance + giro)

**Tarea:** *ejecución de un movimiento planificado*. Dada una posición objetivo (el planificador de
caminos o tú la dais), el robot gira hasta apuntar a ella y avanza hasta llegar, usando solo la
odometría ([docs/odometria.md](../docs/odometria.md)).

## Ejecutar

```bat
conda activate create2
python navegacion\main.py
```

En la página `http://127.0.0.1:8000`:

* Escribe `x` e `y` (metros) y pulsa **Ir**, o **haz clic en el mapa**.
* **Parar** cancela el objetivo; **Salir** termina el programa.
* Ejes: origen donde arranca el robot, `x` hacia delante, `y` hacia la izquierda.

## Cómo funciona

El método `ir_al_objetivo` ([rumba/modos/base.py](../rumba/modos/base.py)) es una máquina de dos fases:

```
            error de rumbo < ANG_OK (5°)
   GIRAR ──────────────────────────────────► AVANZAR
     ▲                                          │
     └────────── error de rumbo > ANG_MAX (20°) ┘
```

| Fase | Qué hace |
|---|---|
| **Girar** | Gira sobre sí mismo hacia el objetivo. Velocidad = `K_GIRO · |error|` limitada entre `V_GIRO_MIN` y `V_GIRO`. |
| **Avanzar** | Velocidad = distancia al objetivo limitada entre `V_AVANCE_MIN` y `V_AVANCE` (frena al llegar), más una corrección `K_CORR · error` que reparte entre las ruedas para mantener el rumbo. |
| **Tramo final** | A menos de `DIST_FINAL` (100 mm) ya no se vuelve a girar: un pequeño desvío lateral daría errores de ángulo enormes. Si el objetivo queda detrás, se considera alcanzado. |
| **Llegada** | A menos de `TOL_DIST` (10 mm) del objetivo se para. |

**Seguridad:** esta tarea usa el modo `directo`: no mira los sensores de proximidad. Si el
parachoques se pulsa, **cancela el objetivo** y se queda parada (`Choque: objetivo cancelado`).
Para evitar obstáculos usa [`evitar_obstaculos`](../evitar_obstaculos/README.md).

## Parámetros (`config.env`)

`V_AVANCE`, `V_AVANCE_MIN`, `V_GIRO`, `V_GIRO_MIN`, `K_GIRO`, `K_CORR`, `TOL_DIST`, `DIST_FINAL`,
`ANG_OK_GRADOS`, `ANG_MAX_GRADOS` y los de odometría (`B`, `DIAMETRO_RUEDA`, `CUENTAS_POR_VUELTA`).

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Crea `TareaObjetivo` en modo `directo`. |
| `ui.html` | Formulario de objetivo, mapa con la línea al objetivo y el estado. |

## Mejoras propuestas

1. **Orientación final.** Hoy solo se llega a (x, y); añadir un `θ` objetivo (girar al terminar) permite
   encadenar movimientos tal como los entregaría un planificador.
2. **Lista de puntos (waypoints)**: ya existe en [`circuito`](../circuito/README.md); se podría fundir con
   esta tarea y dejar `navegacion` como la versión mínima para docencia.
3. **Rampas de aceleración.** Pasar de 0 a 150 mm/s de golpe hace patinar las ruedas y degrada la
   odometría (error no sistemático, tema 3). Limitar el cambio de velocidad por ciclo.
4. **Controlador de rumbo proporcional-integral-derivativo** en lugar del proporcional, con el que se
   puede reducir el sobreimpulso de la corrección de rumbo.
5. **Odometría con punto medio** (`θ + Δθ/2`), ver [docs/odometria.md](../docs/odometria.md).
6. **Reintento tras choque** en vez de cancelar (retroceder y volver a intentar una vez).
