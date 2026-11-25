# Circuito: cola de instrucciones

El script más completo. Es [`evitar_obstaculos`](../evitar_obstaculos/README.md) con una **cola de
instrucciones** que el robot ejecuta en orden, pensado para recorridos repetibles (cuadrado, ida y
vuelta...). Cada "Ir a" usa el modo elegido: parar o rodear con Bug2.

## Ejecutar

```bat
conda activate create2
python circuito\main.py
Elige modo (1/2):
```

Abre `http://127.0.0.1:8000`. El panel de la derecha tiene todo el control.

## Instrucciones

| Instrucción | Qué hace |
|---|---|
| **Ir a (x, y)** m | Va a ese punto con el modo elegido. Clic en el mapa añade una. |
| **Girar N°** | Gira sobre sí mismo N grados según la odometría (`+` izquierda, `−` derecha, admite más de 360°). Precisión `TOL_GIRO_GRADOS`. |

**Plantillas:** *Cuadrado 1 m* e *Ida y vuelta 2 m*.

## Controles

| Botón | Efecto |
|---|---|
| ▶ Ejecutar / Continuar | Empieza (o reanuda) la cola. |
| ■ Parar | Detiene la instrucción en curso; **Continuar** la retoma. |
| Repetir circuito | Al terminar vuelve a la primera instrucción. |
| ↑ / ✕ en cada instrucción | Subirla o quitarla (incluso en marcha). |
| Vaciar cola | Borra todo. |
| ⟲ Reiniciar origen y control | Pone x = y = θ = 0 donde esté el robot, para la cola y devuelve el robot a modo Safe. |
| Borrar rastro del mapa | Limpia el dibujo sin tocar la pose. |
| Salir | Para el robot y cierra el programa. |

## Modo Passive

Si levantas el robot, detecta un desnivel o está en la base, el Open Interface pasa **solo** a modo
Passive e ignora las órdenes de movimiento. La página lo detecta (chip **OI**), muestra un aviso y se
resuelve poniéndolo en el suelo y pulsando **Reiniciar origen y control**.

## Panel de información

* Pose (x, y en metros, θ en grados), estado y chips de modo, choques y modo OI.
* Barras con los 6 light bumpers (`L FL CL CR FR R`).
* Mapa: ruta planificada (naranja, numerada), tramo actual (línea M), recorrido real (azul), choques,
  encuentros H, salidas y un arco naranja con el giro que falta.

## Cómo funciona

`Circuito.paso()` ([main.py](main.py)) en cada ciclo:

1. Atiende los botones pendientes (reiniciar, borrar rastro).
2. Descuenta `dtheta` del giro en curso.
3. Si no hay instrucción activa y se está ejecutando, carga la siguiente.
4. Ejecuta un paso del giro, o del trayecto (delegado en el `Navegador` de [rumba/navegacion.py](../rumba/navegacion.py)).
5. Si una instrucción termina: `llegado` pasa a la siguiente; `fallo` (objetivo inalcanzable) **detiene la
   cola**.

El detalle de los dos modos está en el [README de evitar_obstaculos](../evitar_obstaculos/README.md).

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Clase `Circuito`: cola, instrucciones, reinicio y modo Passive. Pregunta el modo al arrancar. |
| `ui.html` | Panel lateral + mapa. |

## Mejoras propuestas

1. **Guardar y cargar circuitos** (JSON) para no reescribirlos tras cada arranque.
2. **Más instrucciones**: *esperar N s*, *avanzar N m* en relativo, *girar hasta θ absoluto*, *repetir N
   veces* (hoy solo hay un bucle infinito).
3. **Reintentos y salto**: si un "Ir a" es inalcanzable, ofrecer saltarlo en vez de detener la cola.
4. **Reiniciar la odometría al volver al origen** (cierre de lazo) cuando se repite el circuito: el error
   se acumula vuelta tras vuelta.
5. **Editar instrucciones** (cambiar x/y) en lugar de borrar y recrear; arrastrar para reordenar.
6. **Persistir el rastro** y los choques para compararlos entre ejecuciones.
