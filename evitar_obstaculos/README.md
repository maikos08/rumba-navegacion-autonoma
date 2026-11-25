# Navegación evitando obstáculos

Igual que [`navegacion`](../navegacion/README.md) (ir a un punto con odometría), pero usando los
sensores de proximidad del Create 2 para no quedarse atascado. Al arrancar la consola pregunta el modo.

## Ejecutar

```bat
conda activate create2
python evitar_obstaculos\main.py
Elige modo (1/2):
```

La página `http://127.0.0.1:8000` es igual que la de navegación y añade el modo, el contador de
**choques**, la lectura de los 6 light bumpers y, en el mapa, los puntos de choque (negro), los puntos de
encuentro H (naranja) y de salida (morado) y la línea M.

## Modo 1 — Parar y esperar

Va recto al objetivo. Si los light bumpers frontales superan `IR_PARADA` (o se pulsa el parachoques) en
fase de avance, **se para en seco**. Cuando la lectura baja de `IR_LIBRE` durante `ESPERA_LIBRE` (1 s)
continúa. Útil cuando el obstáculo es una persona o algo que se va a apartar.

Girar sobre sí mismo sí está permitido estando parado, porque el robot es redondo.

## Modo 2 — Rodear (Bug2)

Algoritmo **Bug2** (tema 5, algoritmos tipo BUG):

1. Va en línea recta al objetivo siguiendo la **línea M** (inicio → objetivo).
2. Al encontrar un obstáculo (parachoques o light bumpers frontales por encima de `IR_FRENTE`) guarda el
   punto de encuentro **H** y empieza a seguir el contorno con la pared a su izquierda (`LADO=-1`).
3. Sigue la pared hasta **volver a cruzar la línea M** en un punto más cercano al objetivo que H
   (`MEJORA`) y a más de `SEP_H` de H; entonces vuelve a ir recto.
4. Si se aleja de H más de `LEJOS_H` y vuelve a menos de `RADIO_H`, ha dado la vuelta completa: el
   objetivo es **inalcanzable** y se detiene.

Seguimiento de contorno (`seguir_contorno` en [`base.py`](../rumba/modos/base.py), el mismo que usa [`seguir_pared`](../seguir_pared/README.md)):

| Situación | Reacción |
|---|---|
| Pared delante (esquina interior) | Gira sobre sí mismo para alejarse. |
| Pared a un lado | Mantiene `IR_OBJETIVO` en el sensor lateral con un control proporcional (`K_PARED`, máx. `CORR_MAX`). |
| Pared perdida (esquina exterior, puerta) | Avanza despacio en arco hacia ella (`V_BUSCAR`, `V_ARCO`). |
| Algo cerca delante | Frena progresivamente (`IR_LENTO` → `IR_FRENTE`, mínimo `FACTOR_MIN`). |
| Choque con el parachoques | Retrocede `RETRO_CONTORNO` mm y gira `ANG_APARTARSE` para apartarse. |

Límites de seguridad: `CONTORNO_MAX` (40 m de pared) y `TIEMPO_MAX` (600 s) por trayecto.

## Los valores de los light bumpers

Van de 0 a 4095 y **dependen del color y material** del obstáculo (lo oscuro refleja menos IR). Si el
robot no detecta o frena demasiado pronto, ajusta `IR_LENTO`, `IR_FRENTE`, `IR_PARADA`, `IR_LIBRE` en
`config.env`. La página muestra las lecturas en vivo y `primeros_scripts/test_sensores.py` las imprime
por consola.

> `IR_PARADA`/`IR_LIBRE` valen ahora 50/30 (antes este script usaba 40/20). Si prefieres la
> sensibilidad antigua, ponlos en `config.env`.

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Pregunta el modo y crea `TareaObjetivo` con `parar` o `bug2`. |
| `ui.html` | Interfaz con IR en vivo y marcas de Bug2. |
| [`rumba/modos/`](../rumba/modos) | Un archivo por modo (`parar.py`, `bug2.py`). |

## Mejoras propuestas

1. **Dibujar los obstáculos como segmentos** y no solo como puntos de choque: con los 6 IR se puede
   estimar la posición de la pared y construir un mapa de ocupación sencillo.
2. **Elegir el lado de contorno** según dónde esté el objetivo (hoy `LADO` es fijo). Bug2 con el lado
   equivocado da la vuelta larga.
3. **Calibración automática de IR**: un script que mida el valor de fondo y el de contacto con un
   obstáculo claro/oscuro y proponga `IR_*`.
4. **Tangent Bug / VFH**: con sensores de rango (como los IR) permiten rodear sin tocar y con menos
   recorrido que Bug2 (ver tema 5, críticas a los algoritmos tipo bug).
5. **Modo 1 con tiempo máximo**: hoy puede esperar indefinidamente; tras N segundos podría pasar a
   Bug2 automáticamente.
6. **Compensar la deriva** de la odometría al volver a la línea M (la línea M se define con una pose
   que ya tiene error).
7. **Unir en un solo modo** `Parar → rodear`, con el modo 1 como primera reacción.
