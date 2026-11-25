# Limpieza de una habitación (*chocayvuelve*)

El robot recorre una habitación como una aspiradora, sin mapa ni objetivo: avanza en línea recta y, al
encontrar un obstáculo, **lo evita y continúa**. Cumple los dos requisitos de la tarea:

1. **No se queda atascado** ante un obstáculo.
2. **Su movimiento es suficientemente aleatorio**: cada pasada sale en una dirección distinta, así que no
   repite recorrido y acaba pasando por toda la habitación.

## Ejecutar

```bat
conda activate create2
python limpieza\main.py
```

Abre `http://127.0.0.1:8000`. Pon el robot en el suelo y pulsa **▶ Iniciar**; **■ Parar** lo detiene (se puede
volver a iniciar) y **Salir** cierra el programa. La página muestra el recorrido, los choques, el estado y
los 6 light bumpers.

## Cómo funciona

Es el modo `limpieza` ([rumba/modos/limpieza.py](../rumba/modos/limpieza.py)), una máquina de tres estados:

```
            obstáculo (IR o parachoques)
 AVANZAR ───────────────────────────────► [RETROCEDER si chocó] ──► GIRAR (ángulo al azar) ──┐
    ▲                                                                                        │
    └────────────────────────────────────────────────────────────────────────────────────────┘
```

| Estado | Qué hace |
|---|---|
| **Avanzar** | Recto a `V_AVANCE`, frenando al acercarse a algo (como en Bug2: de `IR_LENTO` a `IR_FRENTE`). |
| **Retroceder** | Solo si chocó con el parachoques: `LIMPIEZA_RETRO` mm marcha atrás. Si lo detectó solo el IR, no hace falta: el robot es redondo y puede girar sin tocar. |
| **Girar** | Un ángulo **al azar** entre `LIMPIEZA_ANG_MIN_GRADOS` y `LIMPIEZA_ANG_MAX_GRADOS` (90°–180° por defecto), **a izquierda o derecha al azar**, medido con la odometría. |

### Por qué no se atasca

* **Choques seguidos:** si choca `LIMPIEZA_CHOQUES_ATASCO` veces sin recorrer `LIMPIEZA_LIBRE` mm entre medias
  (esquina, hueco estrecho), da casi media vuelta (180° ± 30°) en lugar de un giro normal.
* **Vigilante de movimiento:** si en `ATASCO_TIEMPO` s se ha movido menos de `ATASCO_DIST` mm, hace una
  **maniobra de escape**: retrocede el doble y gira casi 180°.

### Por qué es aleatorio

El ángulo y el sentido de cada giro salen de un generador de números aleatorios. Con `SEMILLA=0` (por
defecto) cambia en cada ejecución; con otro número es **repetible**, útil para depurar o comparar.

## Parámetros (`config.env`)

`LIMPIEZA_ANG_MIN_GRADOS`, `LIMPIEZA_ANG_MAX_GRADOS`, `LIMPIEZA_RETRO`, `LIMPIEZA_CHOQUES_ATASCO`,
`LIMPIEZA_LIBRE`, `ATASCO_TIEMPO`, `ATASCO_DIST`, `SEMILLA`, y los de velocidad y sensores (`V_AVANCE`,
`IR_LENTO`, `IR_FRENTE`...).

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Arranca `TareaExploracion` con el modo `limpieza`. |
| [`rumba/exploracion.py`](../rumba/exploracion.py) y `exploracion.html` | La tarea (Iniciar / Parar) y su página, compartidas con `seguir_pared`. |

## Mejoras propuestas

1. **Medir la cobertura**: dibujar en el mapa una cuadrícula de celdas ya visitadas y mostrar el % de
   habitación cubierto, para parar cuando se supere un umbral (hoy no tiene fin).
2. **Más azar**: girar también tras una distancia aleatoria aunque no haya obstáculo, para evitar pasillos
   paralelos cuando la habitación es muy regular.
3. **Combinar con `seguir_pared`**: limpiar primero el perímetro y luego el centro al azar.
4. **Parada por batería** o por tiempo (`TIEMPO_MAX`) y vuelta al punto de inicio con la odometría.
5. **Evitar zonas ya cubiertas** usando esa cuadrícula (pasa de aleatorio a *semi*-aleatorio dirigido).
6. **Calibrar los umbrales IR** según el suelo y las paredes (ver [evitar_obstaculos](../evitar_obstaculos/README.md)).
