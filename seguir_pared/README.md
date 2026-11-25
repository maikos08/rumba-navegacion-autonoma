# Exploración reactiva: seguir una pared (*seguirpared*)

El robot **busca una pared y la sigue**. Sin mapa y sin objetivo, como en los algoritmos tipo BUG: lo que
haga la pared lo lleva a otras zonas, así que sirve para explorar un lugar desconocido.

## Ejecutar

```bat
conda activate create2
python seguir_pared\main.py
```

Abre `http://127.0.0.1:8000`. Pulsa **▶ Iniciar**; **■ Parar** lo detiene y **Salir** cierra el programa. El
mapa va dibujando el recorrido (es el "mapa" de lo explorado), los choques y los 6 light bumpers.

## Cómo funciona

Es el modo `seguir_pared` ([rumba/modos/seguir_pared.py](../rumba/modos/seguir_pared.py)):

```
          pared encontrada (IR frontal/lateral o parachoques)
 BUSCAR ──────────────────────────────────────────────────────► SEGUIR
    ▲                                                              │
    └──────── pared perdida más de PARED_PERDIDA_TIEMPO s ─────────┘
```

| Estado | Qué hace |
|---|---|
| **Buscar** | Avanza recto frenando al acercarse a algo, hasta encontrar una pared. |
| **Seguir** | Mantiene `IR_OBJETIVO` en el sensor lateral con un control proporcional (`K_PARED`, máx. `CORR_MAX`). |

El seguimiento (`seguir_contorno`, en [rumba/modos/base.py](../rumba/modos/base.py)) es el mismo que usa
Bug2:

| Situación | Reacción |
|---|---|
| Pared delante (esquina interior) | Gira sobre sí mismo para alejarse, dejando la pared al lado. |
| Pared a un lado | La mantiene a distancia constante. |
| Pared perdida (esquina exterior, puerta) | Arco lento hacia ella para rodearla (`V_BUSCAR`, `V_ARCO`). |
| Algo cerca delante | Frena progresivamente (`IR_LENTO` → `IR_FRENTE`, mínimo `FACTOR_MIN`). |
| Choque con el parachoques | Retrocede `RETRO_CONTORNO` mm y gira `ANG_APARTARSE` para apartarse. |

`LADO=-1` (por defecto) deja la pared a la **izquierda** (el robot gira a la derecha al encontrarla);
`LADO=+1`, a la derecha. Si pierde la pared durante `PARED_PERDIDA_TIEMPO` segundos (espacio abierto) vuelve a
buscar otra en vez de dar círculos.

## Parámetros (`config.env`)

`LADO`, `IR_OBJETIVO`, `IR_PERDIDA`, `K_PARED`, `CORR_MAX`, `V_CONTORNO`, `V_BUSCAR`, `V_ARCO`,
`RETRO_CONTORNO`, `ANG_APARTARSE_GRADOS`, `PARED_PERDIDA_TIEMPO`, y los de sensores (`IR_LENTO`,
`IR_FRENTE`).

> Los valores de los light bumpers dependen del color y del material de la pared: si se aleja o se acerca
> demasiado, ajusta `IR_OBJETIVO`. Ver [evitar_obstaculos](../evitar_obstaculos/README.md).

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Arranca `TareaExploracion` con el modo `seguir_pared`. |
| [`rumba/exploracion.py`](../rumba/exploracion.py) y `exploracion.html` | La tarea (Iniciar / Parar) y su página, compartidas con `limpieza`. |

## Mejoras propuestas

1. **Detectar que ha dado la vuelta completa** (como Bug1/Bug2, con la odometría) y parar o cambiar de
   pared, en lugar de seguir indefinidamente.
2. **Construir un mapa de ocupación** con las lecturas IR a lo largo del recorrido, y dibujar las paredes
   y no solo el camino.
3. **Elegir el lado** automáticamente (la pared más cercana al arrancar) en lugar de `LADO` fijo.
4. **Entrar por las puertas:** detectar huecos (pérdida de pared prolongada con IR frontal libre) y decidir
   si seguir pegado o cruzar.
5. **Control PD** (añadir término derivativo) para reducir el balanceo junto a la pared.
6. **Combinar con `limpieza`**: recorrer el perímetro y luego el centro al azar.
